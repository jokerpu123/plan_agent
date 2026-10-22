package com.plan.service;

import com.plan.dto.TaskAnalysisResult;
import com.plan.entity.Task;
import com.plan.entity.TaskStatus;
import com.plan.entity.User;
import com.plan.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

@Service
@RequiredArgsConstructor
public class TaskAnalysisService {
    private final TaskRepository taskRepository;

    public TaskAnalysisResult analyze(Task incoming, User user) {
        List<String> warnings = new ArrayList<>();
        List<Task> existing = taskRepository.findByUserAndTaskDate(user, incoming.getTaskDate()).stream()
                .filter(task -> incoming.getId() == null || !task.getId().equals(incoming.getId()))
                .filter(task -> task.getStatus() != TaskStatus.CANCELLED)
                .toList();

        int existingMinutes = existing.stream()
                .map(Task::getEstimatedMinutes).filter(value -> value != null && value > 0)
                .mapToInt(Integer::intValue).sum();
        int incomingMinutes = positive(incoming.getEstimatedMinutes());
        int plannedMinutes = existingMinutes + incomingMinutes;
        int capacity = user.getDailyCapacityMinutes() == null ? 480 : user.getDailyCapacityMinutes();
        if (plannedMinutes > capacity) {
            warnings.add("当天预计任务量为 " + plannedMinutes + " 分钟，超过每日容量 " + capacity + " 分钟");
        }

        if (incoming.getStartTime() != null && incoming.getEndTime() != null) {
            if (!incoming.getEndTime().isAfter(incoming.getStartTime())) {
                warnings.add("结束时间必须晚于开始时间");
            } else {
                long slotMinutes = Duration.between(incoming.getStartTime(), incoming.getEndTime()).toMinutes();
                if (incomingMinutes > slotMinutes) {
                    warnings.add("预计用时 " + incomingMinutes + " 分钟，超过安排的时间段 " + slotMinutes + " 分钟");
                }
                existing.stream().filter(this::hasTimeRange).forEach(task -> {
                    if (overlaps(incoming, task)) {
                        warnings.add("与任务“" + task.getContent() + "”（" + shortTime(task.getStartTime())
                                + "-" + shortTime(task.getEndTime()) + "）时间重叠");
                    }
                });
                checkBreak(incoming, existing, user, warnings);
            }
        } else if (incoming.getStartTime() != null || incoming.getEndTime() != null) {
            warnings.add("开始时间和结束时间需要同时设置，才能检测时间冲突");
        }

        if (incoming.getDeadline() != null) {
            LocalDateTime taskStart = incoming.getTaskDate().atTime(
                    incoming.getStartTime() == null ? LocalTime.MIN : incoming.getStartTime());
            if (incoming.getDeadline().isBefore(taskStart)) warnings.add("截止时间早于任务开始时间");
            if (incoming.getDeadline().isBefore(LocalDateTime.now())) warnings.add("截止时间已经过去");
        }

        int remaining = Math.max(0, capacity - existingMinutes);
        if (incomingMinutes > remaining && plannedMinutes <= capacity) {
            warnings.add("预计用时超过当天剩余可安排时间");
        }
        return new TaskAnalysisResult(warnings.isEmpty(), plannedMinutes, capacity, remaining, warnings);
    }

    private void checkBreak(Task incoming, List<Task> existing, User user, List<String> warnings) {
        int minimum = user.getMinimumBreakMinutes() == null ? 15 : user.getMinimumBreakMinutes();
        List<Task> timeline = new ArrayList<>(existing.stream().filter(this::hasTimeRange).toList());
        timeline.add(incoming);
        timeline.sort(Comparator.comparing(Task::getStartTime));
        int position = timeline.indexOf(incoming);
        if (position > 0) checkGap(timeline.get(position - 1), incoming, minimum, warnings);
        if (position < timeline.size() - 1) checkGap(incoming, timeline.get(position + 1), minimum, warnings);
    }

    private void checkGap(Task first, Task second, int minimum, List<String> warnings) {
        long gap = Duration.between(first.getEndTime(), second.getStartTime()).toMinutes();
        if (gap >= 0 && gap < minimum) {
            warnings.add("任务“" + first.getContent() + "”和“" + second.getContent()
                    + "”之间仅休息 " + gap + " 分钟，建议至少 " + minimum + " 分钟");
        }
    }

    private boolean hasTimeRange(Task task) {
        return task.getStartTime() != null && task.getEndTime() != null;
    }

    private boolean overlaps(Task first, Task second) {
        return first.getStartTime().isBefore(second.getEndTime())
                && second.getStartTime().isBefore(first.getEndTime());
    }

    private int positive(Integer value) { return value == null ? 0 : Math.max(0, value); }
    private String shortTime(LocalTime value) { return value.toString().substring(0, 5); }
}
