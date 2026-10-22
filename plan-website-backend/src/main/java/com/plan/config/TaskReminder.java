package com.plan.config;

import com.plan.entity.Task;
import com.plan.entity.ReminderChannel;
import com.plan.entity.TaskStatus;
import com.plan.repository.TaskRepository;
import jakarta.mail.internet.MimeMessage;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.List;

@Component
@RequiredArgsConstructor
public class TaskReminder {
    private static final Logger log = LoggerFactory.getLogger(TaskReminder.class);

    private final TaskRepository taskRepository;
    private final JavaMailSender mailSender;

    @Value("${spring.mail.username:}")
    private String sender;

    /** 每分钟检查未来 24 小时内已经到达提醒时间的任务。 */
    @Scheduled(cron = "0 * * * * *")
    public void sendDueReminders() {
        LocalDateTime now = LocalDateTime.now();
        List<Task> candidates = taskRepository
                .findByReminderEnabledTrueAndReminderSentFalseAndDeadlineBetween(now, now.plusDays(1));
        for (Task task : candidates) {
            int minutes = task.getReminderMinutesBefore() == null ? 30 : task.getReminderMinutesBefore();
            if (task.getDeadline().minusMinutes(minutes).isAfter(now)) continue;
            if (task.getStatus() == TaskStatus.COMPLETED || task.getStatus() == TaskStatus.CANCELLED) continue;
            try {
                if (task.getReminderChannel() == ReminderChannel.SMS) {
                    log.warn("任务 {} 需要短信提醒，但尚未配置短信供应商", task.getId());
                    continue;
                }
                sendEmail(task);
                task.setReminderSent(true);
                taskRepository.save(task);
            } catch (Exception exception) {
                log.error("发送任务 {} 的提醒失败", task.getId(), exception);
            }
        }
    }

    private void sendEmail(Task task) throws Exception {
        if (sender == null || sender.isBlank()) throw new IllegalStateException("未配置发件邮箱");
        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
        helper.setFrom(sender);
        helper.setTo(task.getUser().getEmail());
        helper.setSubject("【计划提醒】" + task.getContent());
        helper.setText("你的任务即将到期：<br/><b>" + escapeHtml(task.getContent())
                + "</b><br/>截止时间：" + task.getDeadline(), true);
        mailSender.send(message);
    }

    private String escapeHtml(String value) {
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
    }
}
