package com.plan.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI planWebsiteOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("计划安排系统 API")
                .description("任务、重复任务、专注计时、统计和智能计划服务接口")
                .version("v1")
                .contact(new Contact().name("Plan Website Team"))
                .license(new License().name("Internal Use")));
    }
}
