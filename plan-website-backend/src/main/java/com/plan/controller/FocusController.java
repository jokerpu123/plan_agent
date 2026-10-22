package com.plan.controller;

import com.plan.dto.FocusStartRequest;
import com.plan.entity.*;
import com.plan.repository.FocusSessionRepository;
import com.plan.repository.TaskRepository;
import com.plan.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.http.MediaType;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping(value = "/api/focus", produces = MediaType.APPLICATION_JSON_VALUE)
@RequiredArgsConstructor
public class FocusController {
    private final FocusSessionRepository focusSessionRepository;
    private final UserRepository userRepository;
    private final TaskRepository taskRepository;

    @GetMapping("/active")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Active focus session"),
            @ApiResponse(responseCode = "204", description = "No active focus session", content = @io.swagger.v3.oas.annotations.media.Content)
    })
    public ResponseEntity<FocusSession> active(@RequestParam String email) {
        User user = userRepository.findByEmail(email).orElseThrow();
        return focusSessionRepository.findFirstByUserAndStatusOrderByStartedAtDesc(user, FocusStatus.RUNNING)
                .map(ResponseEntity::ok).orElseGet(() -> ResponseEntity.noContent().build());
    }

    @GetMapping("/sessions")
    public List<FocusSession> sessions(@RequestParam String email,
                                       @RequestParam String from,
                                       @RequestParam String to) {
        User user = userRepository.findByEmail(email).orElseThrow();
        return focusSessionRepository.findByUserAndStartedAtBetweenOrderByStartedAtDesc(
                user, LocalDate.parse(from).atStartOfDay(), LocalDate.parse(to).plusDays(1).atStartOfDay());
    }

    @PostMapping("/start")
    public ResponseEntity<?> start(@RequestBody FocusStartRequest request) {
        User user = userRepository.findById(request.userId()).orElseThrow();
        if (focusSessionRepository.findFirstByUserAndStatusOrderByStartedAtDesc(user, FocusStatus.RUNNING).isPresent()) {
            return ResponseEntity.badRequest().body("已有正在进行的专注记录");
        }
        Task task = request.taskId() == null ? null : taskRepository.findById(request.taskId()).orElseThrow();
        String title = request.title() == null || request.title().isBlank()
                ? (task == null ? "自由专注" : task.getContent()) : request.title().trim();
        FocusSession session = new FocusSession();
        session.setUser(user);
        session.setTask(task);
        session.setTitle(title);
        session.setStartedAt(LocalDateTime.now());
        return ResponseEntity.ok(focusSessionRepository.save(session));
    }

    @PutMapping("/{id}/stop")
    public ResponseEntity<FocusSession> stop(@PathVariable Long id, @RequestParam(required = false) String note) {
        FocusSession session = focusSessionRepository.findById(id).orElseThrow();
        if (session.getStatus() == FocusStatus.RUNNING) {
            session.finish(LocalDateTime.now());
            session.setNote(note);
            if (session.getTask() != null) {
                Task task = session.getTask();
                int previous = task.getActualMinutes() == null ? 0 : task.getActualMinutes();
                int minutes = (int) Math.ceil(session.getDurationSeconds() / 60.0);
                task.setActualMinutes(previous + minutes);
                if (task.getStatus() == TaskStatus.TODO) task.setStatus(TaskStatus.IN_PROGRESS);
                taskRepository.save(task);
            }
        }
        return ResponseEntity.ok(focusSessionRepository.save(session));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        if (!focusSessionRepository.existsById(id)) return ResponseEntity.notFound().build();
        focusSessionRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
