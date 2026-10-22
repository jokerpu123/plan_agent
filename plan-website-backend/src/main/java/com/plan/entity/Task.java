// 任务实体
package com.plan.entity;

import jakarta.persistence.*;
import lombok.Data;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

@Data
@Entity
@Table(name = "task", uniqueConstraints = @UniqueConstraint(
        name = "uk_task_recurrence_date", columnNames = {"recurring_task_id", "task_date"}))
public class Task {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String content;  // 任务内容
    
    @Column(nullable = false)
    private LocalDate taskDate;  // 任务日期（周计划存该周周一）
    
    private boolean completed = false;  // 是否完成，默认未完成

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private TaskStatus status = TaskStatus.TODO;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private TaskPriority priority = TaskPriority.MEDIUM;

    @Schema(type = "string", format = "time", example = "09:00:00", nullable = true)
    private LocalTime startTime;
    @Schema(type = "string", format = "time", example = "10:00:00", nullable = true)
    private LocalTime endTime;
    @Schema(nullable = true)
    private LocalDateTime deadline;
    @Schema(nullable = true)
    private Integer estimatedMinutes;
    @Schema(nullable = true)
    private Integer actualMinutes;
    @Schema(nullable = true)
    private LocalDateTime completedAt;

    private boolean reminderEnabled = false;

    @Enumerated(EnumType.STRING)
    @Column(length = 16)
    @Schema(nullable = true, description = "提醒渠道；历史数据可能为空")
    private ReminderChannel reminderChannel = ReminderChannel.EMAIL;

    @Schema(nullable = true)
    private Integer reminderMinutesBefore = 30;
    private boolean reminderSent = false;

    /** daily=每日规划，weekly=每周规划 */
    @Column(length = 16)
    private String planType = "daily";
    
    // 多对一关联用户
    @ManyToOne
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "recurring_task_id")
    @com.fasterxml.jackson.annotation.JsonIgnore
    private RecurringTask recurringTask;

    @OneToMany(mappedBy = "task", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("sortOrder ASC, id ASC")
    private List<Subtask> subtasks = new ArrayList<>();

    @PrePersist
    public void prePersist() {
        if (planType == null || planType.isBlank()) {
            planType = "daily";
        }
        if (status == null) status = completed ? TaskStatus.COMPLETED : TaskStatus.TODO;
        completed = status == TaskStatus.COMPLETED;
        if (completed && completedAt == null) completedAt = LocalDateTime.now();
        if (priority == null) priority = TaskPriority.MEDIUM;
        if (reminderChannel == null) reminderChannel = ReminderChannel.EMAIL;
        if (reminderMinutesBefore == null || reminderMinutesBefore < 0) reminderMinutesBefore = 30;
        syncSubtasks();
    }

    @PostLoad
    public void normalizeReminderDefaults() {
        if (reminderChannel == null) reminderChannel = ReminderChannel.EMAIL;
        if (reminderMinutesBefore == null || reminderMinutesBefore < 0) reminderMinutesBefore = 30;
    }

    @PreUpdate
    public void preUpdate() {
        normalizeReminderDefaults();
        completed = status == TaskStatus.COMPLETED;
        if (completed && completedAt == null) completedAt = LocalDateTime.now();
        if (!completed) completedAt = null;
        syncSubtasks();
    }

    public void syncSubtasks() {
        if (subtasks != null) subtasks.forEach(subtask -> subtask.setTask(this));
    }
}
