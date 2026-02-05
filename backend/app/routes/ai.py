from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import User, AIWeeklyReport, Checkin
from app.schemas import AIReportResponse, AIReportGenerate, AIReportTaskResponse, ResponseModel, AILearningData, AICheckinAnalysisRequest, AICheckinAnalysisResponse, AICheckinStats, AICheckinPattern, AICheckinAnomaly
from app.auth import get_current_user, api_key_auth
from app.services.ai import deepseek_client
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


@router.get("/weekly_report/stream")
async def stream_weekly_report(
    week_date: date = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """流式输出周报告分析结果"""
    if not week_date:
        today = date.today()
        week_date = today - timedelta(days=today.weekday())
    
    week_start = week_date
    week_end = week_start + timedelta(days=6)
    
    # 获取打卡数据
    checkins = db.query(Checkin).filter(
        Checkin.user_id == current_user.id,
        Checkin.checkin_date >= week_start,
        Checkin.checkin_date <= week_end
    ).all()
    
    total_hours = sum(c.duration_min for c in checkins) / 60
    checkin_count = len(checkins)
    unique_dates = len(set(c.checkin_date for c in checkins))
    total_days = (week_end - week_start).days + 1
    checkin_rate = (unique_dates / total_days) * 100 if total_days > 0 else 0
    
    score = int(checkin_rate)
    if total_hours > 10:
        score = min(100, score + 10)
    
    # 构建AI分析prompt
    prompt = f"""你作为专业的学习教练AI，请基于以下学习数据，为用户提供详细的周学习评估报告：

分析期间：{week_start} 至 {week_end}
总打卡次数：{checkin_count}次
总学习时长：{total_hours:.1f}小时
打卡率：{checkin_rate:.1f}%

请提供：
1. 学习评分（总分、打卡频率、学习时长、学习稳定性）
2. 学习总结（打卡频率、学习趋势、稳定性）
3. 存在问题
4. 改进建议
5. 推荐学习时长

要求分析详细、具体，避免空泛的描述。"""
    
    def generate():
        # 先输出基本统计数据
        import json
        basic_data = {
            "type": "basic",
            "data": {
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "score": {
                    "total": score,
                    "frequency": int(checkin_rate),
                    "duration": min(100, int(total_hours * 10)),
                    "stability": int(checkin_rate)
                }
            }
        }
        yield f"{json.dumps(basic_data)}\n"
        
        # 使用DeepSeek API进行智能分析
        try:
            stream = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            full_content = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_content += content
                    # 每获取到一定内容就输出一次
                    if len(full_content) > 200:
                        analysis_data = {
                            "type": "analysis",
                            "data": {
                                "content": full_content
                            }
                        }
                        yield f"{json.dumps(analysis_data)}\n"
                        full_content = ""
            
            # 输出剩余内容
            if full_content:
                analysis_data = {
                    "type": "analysis",
                    "data": {
                        "content": full_content
                    }
                }
                yield f"{json.dumps(analysis_data)}\n"
            
            # 输出完成标志
            complete_data = {
                "type": "complete"
            }
            yield f"{json.dumps(complete_data)}\n"
        except Exception as e:
            error_data = {
                "type": "error",
                "data": {
                    "message": str(e)
                }
            }
            yield f"{json.dumps(error_data)}\n"
    
    return StreamingResponse(generate(), media_type="application/json")


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


@router.post("/learning_coach")
async def learning_coach_stream(
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

    def generate():
        stream = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in stream:
            # DeepSeek 的流式内容在这里
            content = chunk.choices[0].delta.content
            if content:
                yield content

    return StreamingResponse(generate(), media_type="text/plain")


@router.post("/checkin_analysis", response_model=ResponseModel)
async def get_checkin_analysis(
    analysis_request: AICheckinAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 设置默认日期范围
    if not analysis_request.start_date:
        analysis_request.start_date = date.today() - timedelta(days=30)
    if not analysis_request.end_date:
        analysis_request.end_date = date.today()
    
    # 获取用户的打卡记录
    checkins = db.query(Checkin).filter(
        Checkin.user_id == current_user.id,
        Checkin.checkin_date >= analysis_request.start_date,
        Checkin.checkin_date <= analysis_request.end_date
    ).order_by(Checkin.checkin_date.asc()).all()
    
    if not checkins:
        return ResponseModel(
            data={
                "period": f"{analysis_request.start_date} 至 {analysis_request.end_date}",
                "stats": {
                    "total_checkins": 0,
                    "total_hours": 0,
                    "avg_daily_hours": 0,
                    "checkin_rate": 0,
                    "on_time_rate": 0,
                    "streak_days": 0,
                    "max_streak": 0,
                    "missed_days": 0,
                    "late_days": 0,
                    "early_days": 0
                },
                "patterns": [],
                "anomalies": [],
                "insights": ["暂无打卡记录"],
                "recommendations": ["建议开始制定学习计划并打卡"],
                "ai_summary": "分析期间内无打卡记录"
            }
        )
    
    # 基础统计分析
    total_checkins = len(checkins)
    total_hours = sum(c.duration_min for c in checkins) / 60
    
    # 计算打卡率
    total_days = (analysis_request.end_date - analysis_request.start_date).days + 1
    checkin_dates = set(c.checkin_date for c in checkins)
    checkin_rate = (len(checkin_dates) / total_days) * 100
    
    # 计算平均每日学习时长
    avg_daily_hours = total_hours / len(checkin_dates) if checkin_dates else 0
    
    # 计算连续打卡天数（简化版本）
    streak_days = 0
    max_streak = 0
    current_streak = 0
    
    for i in range(total_days):
        current_date = analysis_request.start_date + timedelta(days=i)
        if current_date in checkin_dates:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    streak_days = max_streak
    
    # 计算异常打卡情况（简化版本）
    missed_days = total_days - len(checkin_dates)
    
    # 生成洞察和建议
    insights = []
    recommendations = []
    
    if checkin_rate < 50:
        insights.append(f"打卡率较低（{checkin_rate:.1f}%），需要提高学习积极性")
        recommendations.append("建议制定固定的学习计划，培养每日学习习惯")
    
    if avg_daily_hours < 1:
        insights.append("平均每日学习时长偏短，需要增加学习时间")
        recommendations.append("建议每天至少学习1-2小时，逐步增加学习强度")
    
    if streak_days < 7:
        insights.append("连续打卡天数较少，学习连续性有待提高")
        recommendations.append("尝试连续打卡7天以上，形成稳定的学习节奏")
    
    # 生成模式分析（简化版本）
    patterns = []
    if len(checkin_dates) > 5:
        patterns.append({
            "pattern_type": "frequency",
            "description": f"平均每{total_days/len(checkin_dates):.1f}天打卡一次",
            "frequency": len(checkin_dates) / total_days,
            "confidence": 0.8
        })
    
    # 生成异常分析（简化版本）
    anomalies = []
    if missed_days > total_days * 0.3:
        anomalies.append({
            "date": analysis_request.start_date + timedelta(days=total_days//2),
            "type": "missing_pattern",
            "description": f"存在{missed_days}天未打卡，占总天数的{missed_days/total_days*100:.1f}%",
            "severity": "high" if missed_days > total_days * 0.5 else "medium"
        })
    
    # 生成基础总结
    basic_summary = f"在{analysis_request.start_date}至{analysis_request.end_date}期间，共打卡{total_checkins}次，总学习时长{total_hours:.1f}小时，平均每日{avg_daily_hours:.1f}小时，打卡率{checkin_rate:.1f}%。"
    
    # 使用DeepSeek API进行智能分析
    ai_summary = basic_summary
    try:
        # 构建详细的分析prompt
        analysis_prompt = f"""你作为专业的学习教练AI，请基于以下打卡数据进行深度分析：

打卡统计：
- 分析期间：{analysis_request.start_date} 至 {analysis_request.end_date}
- 总打卡次数：{total_checkins}次
- 总学习时长：{total_hours:.1f}小时
- 平均每日学习时长：{avg_daily_hours:.1f}小时
- 打卡率：{checkin_rate:.1f}%
- 最长连续打卡：{streak_days}天
- 未打卡天数：{missed_days}天

请提供：
1. 对当前学习状态的深度分析
2. 识别出的学习模式和规律
3. 发现的问题和改进建议
4. 具体可行的优化方案

要求分析要具体、可操作，避免空泛的建议。"""

        # 使用同步调用
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=2048,
            temperature=0.7
        )
        
        ai_summary = response.choices[0].message.content
        
        # 从AI响应中提取更多洞察和建议
        ai_lines = ai_summary.split('\n')
        for line in ai_lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•')):
                content = line.lstrip('- •').strip()
                if any(keyword in content.lower() for keyword in ['建议', '改进', '优化', '应该']):
                    recommendations.append(content)
                elif any(keyword in content.lower() for keyword in ['问题', '不足', '需要', '缺乏']):
                    insights.append(content)
        
    except Exception as e:
        print(f"AI分析调用失败: {str(e)}")
        # 如果AI分析失败，使用基础总结
    
    return ResponseModel(
        data={
            "period": f"{analysis_request.start_date} 至 {analysis_request.end_date}",
            "stats": {
                "total_checkins": total_checkins,
                "total_hours": round(total_hours, 2),
                "avg_daily_hours": round(avg_daily_hours, 2),
                "checkin_rate": round(checkin_rate, 2),
                "on_time_rate": round(checkin_rate, 2),  # 简化处理
                "streak_days": streak_days,
                "max_streak": max_streak,
                "missed_days": missed_days,
                "late_days": 0,  # 简化处理
                "early_days": 0  # 简化处理
            },
            "patterns": patterns,
            "anomalies": anomalies,
            "insights": insights,
            "recommendations": recommendations,
            "ai_summary": ai_summary
        }
    )
