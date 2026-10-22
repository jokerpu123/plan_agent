package com.plan.service;

import com.plan.entity.FocusSession;
import com.plan.entity.FocusStatus;
import com.plan.entity.Task;
import com.plan.entity.TaskStatus;
import com.plan.entity.User;
import com.plan.dto.StatisticsResult;
import com.plan.repository.FocusSessionRepository;
import com.plan.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class StatisticsService {
    private final TaskRepository taskRepository;
    private final FocusSessionRepository focusSessionRepository;

    public StatisticsResult summarize(User user, LocalDate from, LocalDate to, String planType) {
        String normalizedPlanType = normalizePlanType(planType);
        List<Task> tasks = taskRepository.findByUserAndTaskDateBetweenOrderByTaskDateAscStartTimeAsc(user, from, to)
                .stream()
                .filter(task -> normalizePlanType(task.getPlanType()).equals(normalizedPlanType))
                .toList();
        List<FocusSession> sessions = focusSessionRepository.findByUserAndStartedAtBetweenOrderByStartedAtDesc(
                user, from.atStartOfDay(), to.plusDays(1).atStartOfDay());
        long completed = tasks.stream().filter(this::isCompleted).count();
        long overdue = tasks.stream().filter(task -> !isCompleted(task)
                && task.getDeadline() != null && task.getDeadline().isBefore(java.time.LocalDateTime.now())).count();
        int estimated = tasks.stream().map(Task::getEstimatedMinutes).filter(v -> v != null).mapToInt(Integer::intValue).sum();
        int actual = tasks.stream().map(Task::getActualMinutes).filter(v -> v != null).mapToInt(Integer::intValue).sum();
        long focusSeconds = sessions.stream().filter(s -> s.getStatus() == FocusStatus.COMPLETED)
                .map(FocusSession::getDurationSeconds).filter(v -> v != null).mapToLong(Long::longValue).sum();

        Map<String, Long> statusCounts = tasks.stream().collect(Collectors.groupingBy(
                task -> normalizedStatus(task).name(), LinkedHashMap::new, Collectors.counting()));
        Map<String, Long> priorityCounts = tasks.stream().collect(Collectors.groupingBy(
                task -> task.getPriority() == null ? "MEDIUM" : task.getPriority().name(),
                LinkedHashMap::new, Collectors.counting()));
        Map<String, Map<String, Long>> daily = new LinkedHashMap<>();
        for (LocalDate date = from; !date.isAfter(to); date = date.plusDays(1)) {
            LocalDate current = date;
            long total = tasks.stream().filter(task -> current.equals(task.getTaskDate())).count();
            long done = tasks.stream().filter(task -> current.equals(task.getTaskDate()) && isCompleted(task)).count();
            daily.put(date.toString(), Map.of("total", total, "completed", done));
        }

        return new StatisticsResult(
                from, to, tasks.size(), completed,
                tasks.isEmpty() ? 0 : Math.round(completed * 1000.0 / tasks.size()) / 10.0,
                overdue, estimated, actual, Math.round(focusSeconds / 60.0),
                sessions.stream().filter(s -> s.getStatus() == FocusStatus.COMPLETED).count(),
                statusCounts, priorityCounts, daily);
    }

    private boolean isCompleted(Task task) {
        return task.isCompleted() || task.getStatus() == TaskStatus.COMPLETED;
    }

    private TaskStatus normalizedStatus(Task task) {
        if (task.getStatus() != null) return task.getStatus();
        return task.isCompleted() ? TaskStatus.COMPLETED : TaskStatus.TODO;
    }

    private String normalizePlanType(String planType) {
        return "weekly".equalsIgnoreCase(planType == null ? "" : planType.trim()) ? "weekly" : "daily";
    }
}
