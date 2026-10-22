package com.plan.controller;
import com.plan.entity.User;
import com.plan.dto.StatisticsResult;
import com.plan.repository.UserRepository;
import com.plan.service.StatisticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.MediaType;
import java.time.LocalDate;
import java.util.Map;
@RestController
@RequestMapping(value = "/api/statistics", produces = MediaType.APPLICATION_JSON_VALUE)
@RequiredArgsConstructor
public class StatisticsController {
    private final UserRepository userRepository;
    private final StatisticsService statisticsService;
    @GetMapping
    public StatisticsResult statistics(@RequestParam String email,
                                          @RequestParam String from,
                                          @RequestParam String to,
                                          @RequestParam(required = false, defaultValue = "daily") String planType) {
        User user = userRepository.findByEmail(email).orElseThrow();
        return statisticsService.summarize(user, LocalDate.parse(from), LocalDate.parse(to), planType);
    }
}
