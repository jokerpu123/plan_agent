package com.plan.service;

import com.plan.entity.RecurringTask;
import com.plan.entity.Task;
import com.plan.entity.TaskStatus;
import com.plan.entity.User;
import com.plan.repository.RecurringTaskRepository;
import com.plan.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Service
@RequiredArgsConstructor
public class RecurringTaskService {
    private final RecurringTaskRepository recurringTaskRepository;
    private final TaskRepository taskRepository;

    @Transactional
    public void materializeForUserAndDate(User user, LocalDate date) {
        recurringTaskRepository.findByUserOrderByIdDesc(user).stream()
                .filter(RecurringTask::isActive)
                .filter(rule -> appliesOn(rule, date))
                .forEach(rule -> createOccurrenceIfAbsent(rule, date));
    }

    @Transactional
    public void materializeRange(RecurringTask rule, LocalDate from, LocalDate to) {
        LocalDate start = from.isBefore(rule.getStartDate()) ? rule.getStartDate() : from;
        LocalDate end = rule.getEndDate() != null && to.isAfter(rule.getEndDate()) ? rule.getEndDate() : to;
        for (LocalDate current = start; !current.isAfter(end); current = current.plusDays(1)) {
            if (appliesOn(rule, current)) createOccurrenceIfAbsent(rule, current);
        }
    }

    @Transactional
    public void replaceFutureOccurrences(RecurringTask rule) {
        List<Task> future = taskRepository.findByRecurringTaskIdAndTaskDateGreaterThanEqual(
                rule.getId(), LocalDate.now());
        taskRepository.deleteAll(future);
        LocalDate end = rule.getEndDate() == null ? LocalDate.now().plusYears(1) : rule.getEndDate();
        materializeRange(rule, LocalDate.now(), end);
    }

    @Scheduled(cron = "0 5 0 * * *")
    @Transactional
    public void materializeUpcomingOccurrences() {
        LocalDate today = LocalDate.now();
        List<RecurringTask> rules = recurringTaskRepository
                .findByActiveTrueAndStartDateLessThanEqualAndEndDateGreaterThanEqual(today.plusDays(30), today);
        rules.addAll(recurringTaskRepository
                .findByActiveTrueAndStartDateLessThanEqualAndEndDateIsNull(today.plusDays(30)));
        rules.forEach(rule -> materializeRange(rule, today, today.plusDays(30)));
    }

    private boolean appliesOn(RecurringTask rule, LocalDate date) {
        if (date.isBefore(rule.getStartDate())) return false;
        if (rule.getEndDate() != null && date.isAfter(rule.getEndDate())) return false;
        Set<Integer> weekdays = parseWeekdays(rule.getWeekdays());
        return weekdays.contains(date.getDayOfWeek().getValue());
    }

    private Set<Integer> parseWeekdays(String value) {
        Set<Integer> result = new HashSet<>();
        if (value == null) return result;
        for (String item : value.split(",")) {
            try {
                int day = Integer.parseInt(item.trim());
                if (day >= 1 && day <= 7) result.add(day);
            } catch (NumberFormatException ignored) {
            }
        }
        return result;
    }

    private void createOccurrenceIfAbsent(RecurringTask rule, LocalDate date) {
        if (taskRepository.existsByRecurringTaskIdAndTaskDate(rule.getId(), date)) return;
        Task task = new Task();
        task.setContent(rule.getContent());
        task.setTaskDate(date);
        task.setPlanType("daily");
        task.setStatus(TaskStatus.TODO);
        task.setPriority(rule.getPriority());
        task.setStartTime(rule.getStartTime());
        task.setEndTime(rule.getEndTime());
        task.setEstimatedMinutes(rule.getEstimatedMinutes());
        task.setReminderEnabled(rule.isReminderEnabled());
        task.setReminderChannel(rule.getReminderChannel());
        task.setReminderMinutesBefore(rule.getReminderMinutesBefore());
        if (rule.getStartTime() != null) task.setDeadline(date.atTime(rule.getStartTime()));
        task.setUser(rule.getUser());
        task.setRecurringTask(rule);
        taskRepository.save(task);
    }
}
