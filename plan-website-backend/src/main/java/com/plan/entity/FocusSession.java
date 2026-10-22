package com.plan.entity;

import jakarta.persistence.*;
import lombok.Data;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.Duration;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "focus_session")
public class FocusSession {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "task_id")
    @Schema(nullable = true)
    private Task task;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private LocalDateTime startedAt;

    @Schema(nullable = true)
    private LocalDateTime endedAt;
    @Schema(nullable = true)
    private Long durationSeconds;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 16)
    private FocusStatus status = FocusStatus.RUNNING;

    @Column(length = 500)
    @Schema(nullable = true)
    private String note;

    public void finish(LocalDateTime time) {
        endedAt = time;
        durationSeconds = Math.max(0, Duration.between(startedAt, endedAt).getSeconds());
        status = FocusStatus.COMPLETED;
    }
}
