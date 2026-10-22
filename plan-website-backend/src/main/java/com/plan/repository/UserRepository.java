package com.plan.repository;

import com.plan.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    // 根据邮箱查询用户（登录用）
    Optional<User> findByEmail(String email);
}