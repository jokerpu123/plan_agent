// 用户实体
package com.plan.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.Data;
import io.swagger.v3.oas.annotations.media.Schema;
import java.util.List;

@Data
@Entity
@Table(name = "user")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, nullable = false)
    private String email;  // 登录账号（邮箱）
    
    @JsonIgnore
    @Column(nullable = false)
    private String password;  // 密码（实际开发需加密）

    @Column(length = 32)
    @Schema(nullable = true)
    private String phone;

    /** 用户每天愿意安排给任务的分钟数，默认 8 小时。 */
    @Schema(nullable = true)
    private Integer dailyCapacityMinutes = 480;

    /** 两个连续任务之间建议保留的最小休息分钟数。 */
    @Schema(nullable = true)
    private Integer minimumBreakMinutes = 15;
    
    // 一对多关联任务（序列化时忽略，避免与 Task.user 循环引用）
    @JsonIgnore
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private List<Task> tasks;
}
