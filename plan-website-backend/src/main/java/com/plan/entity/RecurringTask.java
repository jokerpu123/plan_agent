package com.plan.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.Data;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

@Data
@Entity
@Table(name = "recurring_task")
public class RecurringTask {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String content;

    @Column(nullable = false)
    private LocalDate startDate;

    @Schema(nullable = true)
    private LocalDate endDate;

    /** ISO weekday numbers separated by commas, e.g. 1,2,3,4 = Monday-Thursday. */
    @Column(nullable = false, length = 32)
    private String weekdays;

    private boolean active = true;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private TaskPriority priority = TaskPriority.MEDIUM;

    @Schema(type = "string", format = "time", example = "09:00:00", nullable = true)
    private LocalTime startTime;
    @Schema(type = "string", format = "time", example = "10:00:00", nullable = true)
    private LocalTime endTime;
    @Schema(nullable = true)
    private Integer estimatedMinutes;
    private boolean reminderEnabled = false;

    @Enumerated(EnumType.STRING)
    @Column(length = 16)
    @Schema(nullable = true, description = "提醒渠道；历史数据可能为空")
    private ReminderChannel reminderChannel = ReminderChannel.EMAIL;

    @Schema(nullable = true)
    private Integer reminderMinutesBefore = 30;

    @ManyToOne(fetch = FetchType.EAGER, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @JsonIgnore
    @OneToMany(mappedBy = "recurringTask")
    private List<Task> generatedTasks = new ArrayList<>();

    @PrePersist
    @PreUpdate
    @PostLoad
    public void normalize() {
        if (priority == null) priority = TaskPriority.MEDIUM;
        if (reminderChannel == null) reminderChannel = ReminderChannel.EMAIL;
        if (reminderMinutesBefore == null || reminderMinutesBefore < 0) reminderMinutesBefore = 30;
    }
}
