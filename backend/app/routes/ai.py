from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, AIWeeklyReport, Checkin
from app.schemas import AIReportResponse, AIReportGenerate, AIReportTaskResponse, ResponseModel, AILearningData
from app.auth import get_current_user, api_key_auth
from datetime import date, datetime, timedelta
import uuid
import ollama

router = APIRouter(prefix="/ai", tags=["AI学习评估"])


@router.get("/weekly_report", response_model=ResponseModel)
async def get_weekly_report(
    week_date: date = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not week_date:
        today = date.today()
        week_date = today - timedelta(days=today.weekday())
    
    week_start = week_date
    week_end = week_start + timedelta(days=6)
    
    report = db.query(AIWeeklyReport).filter(
        AIWeeklyReport.user_id == current_user.id,
        AIWeeklyReport.week_start == week_start
    ).first()
    
    if not report:
        return ResponseModel(
            data={
                "week_start": week_start,
                "week_end": week_end,
                "generated_at": None,
                "score": {
                    "total": 0,
                    "frequency": 0,
                    "duration": 0,
                    "stability": 0
                },
                "summary": {
                    "checkin_frequency": "暂无数据",
                    "learning_trend": "暂无数据",
                    "stability_level": "暂无数据"
                },
                "issues": ["本周暂无学习记录"],
                "suggestions": ["建议开始制定学习计划并打卡"],
                "recommended_hours": 1.5
            }
        )
    
    import json
    
    return ResponseModel(
        data={
            "week_start": report.week_start,
            "week_end": report.week_end,
            "generated_at": report.created_at,
            "score": {
                "total": report.score,
                "frequency": 80,
                "duration": 75,
                "stability": 70
            },
            "summary": {
                "checkin_frequency": "本周打卡频率较高",
                "learning_trend": "学习时长稳步增长",
                "stability_level": "学习稳定性良好"
            },
            "issues": json.loads(report.issues) if isinstance(report.issues, str) else [],
            "suggestions": json.loads(report.suggestions) if isinstance(report.suggestions, str) else [],
            "recommended_hours": 2.0
        }
    )


@router.post("/generate_report", response_model=ResponseModel)
async def generate_report(
    report_data: AIReportGenerate,
    api_key_obj = Depends(api_key_auth),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == report_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    existing_report = db.query(AIWeeklyReport).filter(
        AIWeeklyReport.user_id == report_data.user_id,
        AIWeeklyReport.week_start == report_data.week_start
    ).first()
    
    if existing_report:
        return ResponseModel(
            data={
                "task_id": str(uuid.uuid4()),
                "status": "completed",
                "estimated_time": 0
            }
        )
    
    checkins = db.query(Checkin).filter(
        Checkin.user_id == report_data.user_id,
        Checkin.checkin_date >= report_data.week_start,
        Checkin.checkin_date <= report_data.week_end
    ).all()
    
    total_hours = sum(c.duration_min for c in checkins) / 60
    checkin_count = len(checkins)
    
    unique_dates = len(set(c.checkin_date for c in checkins))
    total_days = (report_data.week_end - report_data.week_start).days + 1
    checkin_rate = (unique_dates / total_days) * 100 if total_days > 0 else 0
    
    score = int(checkin_rate)
    if total_hours > 10:
        score = min(100, score + 10)
    
    import json
    
    issues = []
    suggestions = []
    
    if checkin_count < 3:
        issues.append("本周打卡次数较少")
        suggestions.append("建议增加打卡频率，每天至少打卡一次")
    
    if total_hours < 5:
        issues.append("本周学习时长不足")
        suggestions.append("建议每天增加学习时间，目标每周10小时以上")
    
    if checkin_rate < 50:
        issues.append("打卡频率不稳定")
        suggestions.append("建议制定固定学习时间，培养学习习惯")
    
    new_report = AIWeeklyReport(
        user_id=report_data.user_id,
        week_start=report_data.week_start,
        week_end=report_data.week_end,
        score=score,
        summary="本周学习情况分析",
        issues=json.dumps(issues, ensure_ascii=False),
        suggestions=json.dumps(suggestions, ensure_ascii=False)
    )
    
    db.add(new_report)
    db.commit()
    
    return ResponseModel(
        data={
            "task_id": str(uuid.uuid4()),
            "status": "processing",
            "estimated_time": 5
        }
    )


@router.post("/learning_coach", response_model=ResponseModel)
async def get_learning_coach(
    learning_data: AILearningData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 构建prompt
    prompt = f"""你作为专业的学习教练AI，核心目标是帮助用户实现"可执行化"学习，避免泛泛而谈的建议。

请基于以下学习数据，为用户提供系统化的学习指导，具体包括：
1）精准的学习状态评估（基于实际数据，避免空泛描述）
2）科学的下一阶段学习路线建议（需具备可操作性）
3）详细的未来一周具体任务安排（需明确具体行动项）

【输出格式必须严格按照下面结构】
————————————
【一、学习状态评估】
- 3~5 条要点（基于提供的学习数据，每条评估需包含数据支撑和具体分析）

【二、下一阶段学习路线建议】
- 1条总体方向建议（需与考研数学目标直接相关）
- 2~3 条阶段拆解建议（需体现循序渐进的学习逻辑，如：基础巩固→专题强化→综合应用等阶段划分）

【三、未来一周任务安排】
请给出7天的详细学习安排，每天内容必须包含：
- 学习重点（具体知识点或任务，需明确具体内容）
- 建议时长（精确到0.5小时的时间分配）
- 学习方式（明确具体方法，如：观看基础视频/完成XX章节习题/整理错题本/进行模拟测试/制作知识点思维导图等）

————————————
【学习数据】
- 学习目标：{learning_data.learning_goal}
- 本周总学习时长：{learning_data.weekly_total_hours}小时
- 平均每日学习时长：{learning_data.average_daily_hours}小时
- 目标每日学习时长：{learning_data.target_daily_hours}小时
- 连续打卡天数：{learning_data.consecutive_checkin_days}天
- 漏打卡天数：{learning_data.missed_checkin_days}天
"""
    
    try:
        # 调用ollama模型
        response = ollama.chat(
            model="qwen3:8b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # 解析响应
        ai_response = response["message"]["content"]
        
        # 构建返回数据
        return ResponseModel(
            data={
                "ai_response": ai_response
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"调用AI模型失败: {str(e)}"
        )
