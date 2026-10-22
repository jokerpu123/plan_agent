package com.plan.repository;

import com.plan.entity.RecurringTask;
import com.plan.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDate;
import java.util.List;

public interface RecurringTaskRepository extends JpaRepository<RecurringTask, Long> {
    List<RecurringTask> findByUserOrderByIdDesc(User user);
    List<RecurringTask> findByActiveTrueAndStartDateLessThanEqualAndEndDateGreaterThanEqual(
            LocalDate startDate, LocalDate endDate);
    List<RecurringTask> findByActiveTrueAndStartDateLessThanEqualAndEndDateIsNull(LocalDate date);
}
