package com.plan.dto;

import java.util.List;

public record TaskAnalysisResult(
        boolean reasonable,
        int plannedMinutes,
        int capacityMinutes,
        int remainingMinutes,
        List<String> warnings
) {
}
