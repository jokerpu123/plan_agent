package com.plan.controller;

import com.plan.dto.AuthRequest;
import com.plan.dto.TaskAnalysisResult;
import com.plan.entity.Task;
import com.plan.entity.TaskStatus;
import com.plan.entity.RecurringTask;
import com.plan.entity.Subtask;
import com.plan.entity.User;
import com.plan.repository.RecurringTaskRepository;
import com.plan.repository.SubtaskRepository;
import com.plan.repository.TaskRepository;
import com.plan.repository.UserRepository;
import com.plan.service.RecurringTaskService;
import com.plan.service.TaskAnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@CrossOrigin(origins = {
        "http://localhost:8080",
        "http://localhost:8082",
        "http://47.109.192.61:6888"
})
public class PlanController {

    private final UserRepository userRepository;
    private final TaskRepository taskRepository;
    private final RecurringTaskRepository recurringTaskRepository;
    private final SubtaskRepository subtaskRepository;
    private final RecurringTaskService recurringTaskService;
    private final TaskAnalysisService taskAnalysisService;

    // 登录接口
    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody AuthRequest request) {
        if (request.getEmail() == null || request.getEmail().isBlank()
                || request.getPassword() == null || request.getPassword().isBlank()) {
            return ResponseEntity.badRequest().body("邮箱和密码不能为空");
        }
        String email = request.getEmail().trim();
        Optional<User> user = userRepository.findByEmail(email);
        if (user.isPresent() && user.get().getPassword().equals(request.getPassword())) {
            return ResponseEntity.ok(user.get());
        }
        return ResponseEntity.badRequest().body("账号或密码错误");
    }

    // 注册接口（方便测试）
    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody AuthRequest request) {
        if (request.getEmail() == null || request.getEmail().isBlank()
                || request.getPassword() == null || request.getPassword().isBlank()) {
            return ResponseEntity.badRequest().body("邮箱和密码不能为空");
        }
        String email = request.getEmail().trim();
        if (userRepository.findByEmail(email).isPresent()) {
            return ResponseEntity.badRequest().body("该邮箱已注册，请直接登录");
        }
        User user = new User();
        user.setEmail(email);
        user.setPassword(request.getPassword());
        return ResponseEntity.ok(userRepository.save(user));
    }

    // 获取指定用户指定日期的任务（planType: daily | weekly，默认 daily）
    @GetMapping("/tasks")
    public ResponseEntity<List<Task>> getTasks(
            @RequestParam String email,
            @RequestParam String date,
            @RequestParam(required = false, defaultValue = "daily") String planType) {
        User user = userRepository.findByEmail(email).orElseThrow();
        LocalDate taskDate = LocalDate.parse(date);
        String type = normalizePlanType(planType);
        if ("daily".equals(type)) recurringTaskService.materializeForUserAndDate(user, taskDate);
        List<Task> tasks = taskRepository.findByUserAndTaskDate(user, taskDate).stream()
                .filter(t -> normalizePlanType(t.getPlanType()).equals(type))
                .toList();
        return ResponseEntity.ok(tasks);
    }

    // 添加/修改任务
    @PostMapping("/task")
    public ResponseEntity<Task> saveTask(@RequestBody Task task) {
        if (task.getUser() == null || task.getUser().getId() == null) {
            return ResponseEntity.badRequest().build();
        }
        User user = userRepository.findById(task.getUser().getId()).orElseThrow();
        task.setUser(user);
        task.setPlanType(normalizePlanType(task.getPlanType()));
        task.syncSubtasks();
        return ResponseEntity.ok(taskRepository.save(task));//sava方法继承自JpaRepository,如果没有task的id，则添加，否则修改
    }

    @PostMapping("/task/analyze")
    public ResponseEntity<TaskAnalysisResult> analyzeTask(@RequestBody Task task) {
        if (task.getUser() == null || task.getUser().getId() == null || task.getTaskDate() == null) {
            return ResponseEntity.badRequest().build();
        }
        User user = userRepository.findById(task.getUser().getId()).orElseThrow();
        return ResponseEntity.ok(taskAnalysisService.analyze(task, user));

    }
//return ResponseEntity.ok(taskAnalysisService.analyze(task, user));转换后的响应大致是：
//HTTP/1.1 200 OK
//Content-Type: application/json
//{
//  "reasonable": false,
//  "plannedMinutes": 540,
//  "capacityMinutes": 480,
//  "remainingMinutes": 30,
//  "warnings": [
//    "当天任务量超过每日容量",
//    "与任务“健身”时间重叠"
//]
//}
//return ResponseEntity.badRequest().build();转换后的响应大致是：
//HTTP/1.1 400 Bad Request
//Content-Type: application/json
//{
//  "timestamp": "2023-10-01T12:00:00.000+00:00",
//  "status": 400,
//  "error": "Bad Request",
//  "message": "Invalid request body"
//}

    @PutMapping("/task/{id}")
    public ResponseEntity<Task> updateTask(@PathVariable Long id, @RequestBody Task incoming) {
        Task task = taskRepository.findById(id).orElseThrow();
        task.setContent(incoming.getContent());
        task.setTaskDate(incoming.getTaskDate());
        task.setPlanType(normalizePlanType(incoming.getPlanType()));
        task.setStatus(incoming.getStatus());
        task.setPriority(incoming.getPriority());
        task.setStartTime(incoming.getStartTime());
        task.setEndTime(incoming.getEndTime());
        task.setDeadline(incoming.getDeadline());
        task.setEstimatedMinutes(incoming.getEstimatedMinutes());
        task.setActualMinutes(incoming.getActualMinutes());
        task.setReminderEnabled(incoming.isReminderEnabled());
        task.setReminderChannel(incoming.getReminderChannel());
        task.setReminderMinutesBefore(incoming.getReminderMinutesBefore());
        task.setReminderSent(false);
        task.getSubtasks().clear();
        if (incoming.getSubtasks() != null) {
            for (int i = 0; i < incoming.getSubtasks().size(); i++) {
                Subtask item = incoming.getSubtasks().get(i);
                item.setId(null);
                item.setSortOrder(i);
                item.setTask(task);
                task.getSubtasks().add(item);
            }
        }
        return ResponseEntity.ok(taskRepository.save(task));
    }

    private static String normalizePlanType(String planType) {
        if (planType == null || planType.isBlank()) {
            return "daily";
        }
        String type = planType.trim().toLowerCase();
        return "weekly".equals(type) ? "weekly" : "daily";
    }

    // 标记任务完成/未完成
    @PutMapping("/task/{id}/complete")
    public ResponseEntity<Task> completeTask(@PathVariable Long id, @RequestParam boolean completed) {
        Task task = taskRepository.findById(id).orElseThrow();
        task.setCompleted(completed);
        task.setStatus(completed ? TaskStatus.COMPLETED : TaskStatus.TODO);
        return ResponseEntity.ok(taskRepository.save(task));
    }

    @PutMapping("/task/{id}/status")
    public ResponseEntity<Task> updateTaskStatus(@PathVariable Long id, @RequestParam TaskStatus status) {
        Task task = taskRepository.findById(id).orElseThrow();
        task.setStatus(status);
        task.setCompleted(status == TaskStatus.COMPLETED);
        return ResponseEntity.ok(taskRepository.save(task));
    }

    @PutMapping("/subtask/{id}/complete")
    public ResponseEntity<Subtask> completeSubtask(@PathVariable Long id, @RequestParam boolean completed) {
        Subtask subtask = subtaskRepository.findById(id).orElseThrow();
        subtask.setCompleted(completed);
        return ResponseEntity.ok(subtaskRepository.save(subtask));
    }

    // 删除任务
    @DeleteMapping("/task/{id}")
    public ResponseEntity<Void> deleteTask(@PathVariable Long id) {
        if (!taskRepository.existsById(id)) {
            return ResponseEntity.notFound().build();
        }
        taskRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/recurring-tasks")
    public ResponseEntity<List<RecurringTask>> getRecurringTasks(@RequestParam String email) {
        User user = userRepository.findByEmail(email).orElseThrow();
        return ResponseEntity.ok(recurringTaskRepository.findByUserOrderByIdDesc(user));
    }

    @PostMapping("/recurring-task")
    public ResponseEntity<RecurringTask> createRecurringTask(@RequestBody RecurringTask recurringTask) {
        if (recurringTask.getUser() == null || recurringTask.getUser().getId() == null
                || recurringTask.getContent() == null || recurringTask.getContent().isBlank()
                || recurringTask.getStartDate() == null || recurringTask.getWeekdays() == null
                || recurringTask.getWeekdays().isBlank()) {
            return ResponseEntity.badRequest().build();
        }
        User user = userRepository.findById(recurringTask.getUser().getId()).orElseThrow();
        recurringTask.setId(null);
        recurringTask.setUser(user);
        RecurringTask saved = recurringTaskRepository.save(recurringTask);
        LocalDate generationEnd = saved.getEndDate() == null
                ? saved.getStartDate().plusYears(1) : saved.getEndDate();
        recurringTaskService.materializeRange(saved, saved.getStartDate(), generationEnd);
        return ResponseEntity.ok(saved);
    }

    @PutMapping("/recurring-task/{id}")
    public ResponseEntity<RecurringTask> updateRecurringTask(
            @PathVariable Long id, @RequestBody RecurringTask incoming) {
        RecurringTask rule = recurringTaskRepository.findById(id).orElseThrow();
        rule.setContent(incoming.getContent());
        rule.setStartDate(incoming.getStartDate());
        rule.setEndDate(incoming.getEndDate());
        rule.setWeekdays(incoming.getWeekdays());
        rule.setActive(incoming.isActive());
        rule.setPriority(incoming.getPriority());
        rule.setStartTime(incoming.getStartTime());
        rule.setEndTime(incoming.getEndTime());
        rule.setEstimatedMinutes(incoming.getEstimatedMinutes());
        rule.setReminderEnabled(incoming.isReminderEnabled());
        rule.setReminderChannel(incoming.getReminderChannel());
        rule.setReminderMinutesBefore(incoming.getReminderMinutesBefore());
        RecurringTask saved = recurringTaskRepository.save(rule);
        recurringTaskService.replaceFutureOccurrences(saved);
        return ResponseEntity.ok(saved);
    }

    @DeleteMapping("/recurring-task/{id}")
    public ResponseEntity<Void> deleteRecurringTask(@PathVariable Long id) {
        RecurringTask rule = recurringTaskRepository.findById(id).orElseThrow();
        taskRepository.deleteAll(taskRepository.findByRecurringTaskIdAndTaskDateGreaterThanEqual(id, LocalDate.now()));
        recurringTaskRepository.delete(rule);
        return ResponseEntity.noContent().build();
    }
}
