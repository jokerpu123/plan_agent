package com.plan.dto;

import java.time.LocalDate;
import java.util.Map;

public record StatisticsResult(
        LocalDate from,
        LocalDate to,
        int totalTasks,
        long completedTasks,
        double completionRate,
        long overdueTasks,
        int estimatedMinutes,
        int actualMinutes,
        long focusMinutes,
        long focusSessions,
        Map<String, Long> statusCounts,
        Map<String, Long> priorityCounts,
        Map<String, Map<String, Long>> daily
) {
}
