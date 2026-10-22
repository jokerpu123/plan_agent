package com.plan.repository;

import com.plan.entity.FocusSession;
import com.plan.entity.FocusStatus;
import com.plan.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

public interface FocusSessionRepository extends JpaRepository<FocusSession, Long> {
    Optional<FocusSession> findFirstByUserAndStatusOrderByStartedAtDesc(User user, FocusStatus status);
    List<FocusSession> findByUserAndStartedAtBetweenOrderByStartedAtDesc(
            User user, LocalDateTime from, LocalDateTime to);
}
