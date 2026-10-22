package com.plan.repository;

import com.plan.entity.Task;
import com.plan.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

public interface TaskRepository extends JpaRepository<Task, Long> {
    ////一个参数 Task：指定这个 Repository 操作的实体类（对应数据库的task表）；第二个参数 Long：指定Task实体的主键类型
    // 根据邮箱查询用户（登录用）
    // 根据用户+日期查询任务
    List<Task> findByUserAndTaskDate(User user, LocalDate taskDate);
    
    // 根据日期+完成状态查询任务（提醒用）
    List<Task> findByTaskDateAndCompleted(LocalDate taskDate, boolean completed);

    boolean existsByRecurringTaskIdAndTaskDate(Long recurringTaskId, LocalDate taskDate);

    List<Task> findByReminderEnabledTrueAndReminderSentFalseAndDeadlineBetween(
            LocalDateTime from, LocalDateTime to);

    List<Task> findByRecurringTaskIdAndTaskDateGreaterThanEqual(Long recurringTaskId, LocalDate date);

    List<Task> findByUserAndTaskDateBetweenOrderByTaskDateAscStartTimeAsc(
            User user, LocalDate from, LocalDate to);
}
