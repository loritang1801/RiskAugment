package com.riskcontrol.config;

import com.riskcontrol.entity.RiskCase;
import com.riskcontrol.entity.User;
import com.riskcontrol.entity.AIDecisionRecord;
import com.riskcontrol.entity.PromptTemplate;
import com.riskcontrol.repository.RiskCaseRepository;
import com.riskcontrol.repository.UserRepository;
import com.riskcontrol.repository.AIDecisionRecordRepository;
import com.riskcontrol.repository.PromptTemplateRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

@Slf4j
@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {
    private static final int TARGET_RISK_CASE_COUNT = 120;
    private static final int TARGET_DECISION_CASE_COUNT = 80;
    private static final String DEFAULT_DEMO_PASSWORD_HASH = "$2a$10$mki27e48XpR8ALAr125quuBaQerDzF82xHeJK7srY76wZHuncfMIi"; // admin123

    private final UserRepository userRepository;
    private final RiskCaseRepository riskCaseRepository;
    private final AIDecisionRecordRepository aiDecisionRecordRepository;
    private final PromptTemplateRepository promptTemplateRepository;

    @Override
    public void run(String... args) throws Exception {
        log.info("Starting data initialization...");

        try {
            // Initialize each domain independently to avoid partial-empty datasets
            initializeUsers();
            initializePromptTemplates();
            initializeRiskCases();
            log.info("Data initialization completed successfully!");
        } catch (Exception e) {
            log.error("Error during data initialization", e);
            // Continue anyway - don't fail the application startup
        }
    }

    private void initializeUsers() {
        log.info("Ensuring default users (admin/reviewer1/analyst1)...");

        upsertDefaultUser("admin", "admin@example.com", "Administrator", "ADMIN");
        upsertDefaultUser("reviewer1", "reviewer1@example.com", "Reviewer 1", "REVIEWER");
        upsertDefaultUser("analyst1", "analyst1@example.com", "Analyst 1", "ANALYST");

        log.info("Default users ensured. Current user count={}", userRepository.count());
    }

    private void upsertDefaultUser(String username, String email, String fullName, String role) {
        User user = userRepository.findByUsername(username).orElseGet(() -> User.builder().username(username).build());
        user.setEmail(email);
        user.setFullName(fullName);
        user.setRole(role);
        user.setStatus("ACTIVE");
        user.setPasswordHash(DEFAULT_DEMO_PASSWORD_HASH);
        userRepository.save(user);
    }

    private void initializePromptTemplates() {
        log.info("Ensuring prompt templates...");

        boolean createdAny = false;

        if (!promptTemplateRepository.existsByVersion("v1")) {
            PromptTemplate v1 = PromptTemplate.builder()
                    .version("v1")
                    .systemPrompt("You are a risk analysis expert specializing in financial fraud detection. Your task is to analyze transaction cases and provide risk assessments.")
                    .userPromptTemplate("Analyze the following transaction case and provide a risk assessment:\n\nTransaction Details:\n{transaction_details}\n\nSimilar Historical Cases:\n{similar_cases}\n\nProvide your analysis in JSON format with: risk_level, confidence_score, key_risk_points, suggested_action.")
                    .description("Initial version - Basic risk analysis")
                    .isActive(true)
                    .build();
            promptTemplateRepository.save(v1);
            createdAny = true;
            log.info("Prompt template v1 created");
        }

        if (!promptTemplateRepository.existsByVersion("v2")) {
            PromptTemplate v2 = PromptTemplate.builder()
                    .version("v2")
                    .systemPrompt("You are an advanced risk analysis expert with deep knowledge of fraud patterns and regulatory requirements. Provide comprehensive risk assessments.")
                    .userPromptTemplate("Analyze the following transaction case with enhanced risk dimensions:\n\nTransaction Details:\n{transaction_details}\n\nSimilar Historical Cases:\n{similar_cases}\n\nRule Engine Results:\n{rule_results}\n\nProvide detailed analysis in JSON format.")
                    .description("Enhanced version - Improved accuracy")
                    .isActive(false)
                    .build();
            promptTemplateRepository.save(v2);
            createdAny = true;
            log.info("Prompt template v2 created");
        }

        // Ensure at least one active template exists
        if (promptTemplateRepository.findByIsActiveTrue().isEmpty()) {
            promptTemplateRepository.findByVersion("v1").ifPresent(template -> {
                template.setIsActive(true);
                promptTemplateRepository.save(template);
            });
        }

        if (!createdAny) {
            log.info("Prompt templates already exist; no missing default versions");
        }
    }

    private void initializeRiskCases() {
        long existingCount = riskCaseRepository.count();
        if (existingCount >= TARGET_RISK_CASE_COUNT) {
            log.info("Risk cases already meet target count ({}), skipping initialization", existingCount);
            initializeAIDecisions();
            return;
        }

        log.info("Initializing risk cases... existing={}, target={}", existingCount, TARGET_RISK_CASE_COUNT);

        String[][] caseData = {
                {"TXN001", "5000", "USD", "US", "LOW", "existing_user", "LOW", "PENDING", "0.25"},
                {"TXN002", "15000", "USD", "CN", "MEDIUM", "new_user", "MEDIUM", "ANALYZING", "0.55"},
                {"TXN003", "50000", "USD", "RU", "HIGH", "vip_user", "HIGH", "PENDING", "0.85"},
                {"TXN004", "3000", "EUR", "DE", "LOW", "existing_user", "LOW", "APPROVED", "0.15"},
                {"TXN005", "25000", "GBP", "GB", "MEDIUM", "new_user", "MEDIUM", "REJECTED", "0.65"},
                {"TXN006", "8000", "USD", "JP", "LOW", "existing_user", "LOW", "PENDING", "0.30"},
                {"TXN007", "45000", "USD", "IN", "HIGH", "new_user", "HIGH", "ANALYZING", "0.80"},
                {"TXN008", "12000", "EUR", "FR", "MEDIUM", "existing_user", "MEDIUM", "PENDING", "0.50"},
                {"TXN009", "60000", "USD", "BR", "HIGH", "vip_user", "HIGH", "PENDING", "0.90"},
                {"TXN010", "2000", "USD", "CA", "LOW", "new_user", "LOW", "APPROVED", "0.20"}
        };

        com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
        
        int created = 0;
        if (existingCount == 0) {
            for (int i = 0; i < caseData.length; i++) {
                try {
                    String[] data = caseData[i];
                    
                    // Create diverse risk features JSON based on case characteristics
                    com.fasterxml.jackson.databind.node.ObjectNode riskFeatures = mapper.createObjectNode();
                    
                    // Device fingerprint - varies by case
                    riskFeatures.put("device_fingerprint", "fp_" + data[0] + "_" + System.nanoTime());
                    
                    // IP address - varies by country
                    String ipPrefix = getIPPrefixByCountry(data[3]);
                    riskFeatures.put("ip_address", ipPrefix + "." + (100 + i) + "." + (i * 10));
                    
                    // User behavior score - varies by user type
                    int behaviorScore = calculateBehaviorScore(data[5], data[4]);
                    riskFeatures.put("user_behavior_score", behaviorScore);
                    
                    // Additional risk indicators
                    riskFeatures.put("transaction_velocity", (i % 3) + 1);  // 1-3 transactions per hour
                    riskFeatures.put("geolocation_mismatch", i % 2 == 0);  // Some have location mismatch
                    riskFeatures.put("device_age_days", 30 + (i * 10));  // Device age varies
                    
                    RiskCase riskCase = RiskCase.builder()
                            .bizTransactionId(data[0])
                            .amount(new BigDecimal(data[1]))
                            .currency(data[2])
                            .country(data[3])
                            .deviceRisk(data[4])
                            .userLabel(data[5])
                            .riskLevel(data[6])
                            .riskStatus(data[7])
                            .riskScore(new BigDecimal(data[8]))
                            .riskFeatures(riskFeatures)
                            .build();

                    riskCaseRepository.save(riskCase);
                    created++;
                } catch (Exception e) {
                    log.error("Error creating risk case", e);
                }
            }
            existingCount = riskCaseRepository.count();
        }

        int toGenerate = (int) Math.max(0, TARGET_RISK_CASE_COUNT - existingCount);
        for (int i = 0; i < toGenerate; i++) {
            try {
                int seq = (int) existingCount + i + 1;
                RiskCase generated = buildSyntheticRiskCase(seq, mapper);
                riskCaseRepository.save(generated);
                created++;
            } catch (Exception e) {
                log.error("Error generating synthetic risk case", e);
            }
        }

        log.info("Risk cases initialized/backfilled: {} new cases created, total={}", created, riskCaseRepository.count());

        initializeAIDecisions();
    }

    private RiskCase buildSyntheticRiskCase(int seq, com.fasterxml.jackson.databind.ObjectMapper mapper) {
        String[] currencies = {"USD", "EUR", "GBP", "CNY", "JPY"};
        String[] countries = {"US", "CN", "GB", "DE", "JP", "IN", "BR", "CA", "SG", "FR"};
        String[] deviceRisks = {"LOW", "MEDIUM", "HIGH"};
        String[] userLabels = {"existing_user", "new_user", "vip_user", "suspicious"};
        String[] statuses = {"PENDING", "ANALYZING", "APPROVED", "REJECTED"};

        ThreadLocalRandom random = ThreadLocalRandom.current();
        String currency = currencies[seq % currencies.length];
        String country = countries[(seq * 3) % countries.length];
        String deviceRisk = deviceRisks[(seq + 1) % deviceRisks.length];
        String userLabel = userLabels[(seq + 2) % userLabels.length];
        String riskLevel = deviceRisk.equals("HIGH") || "suspicious".equals(userLabel) ? "HIGH" :
                (deviceRisk.equals("MEDIUM") ? "MEDIUM" : "LOW");
        String riskStatus = statuses[seq % statuses.length];

        double amountBase = 1200 + (seq % 90) * 850;
        double amountNoise = random.nextDouble(0, 700);
        BigDecimal amount = BigDecimal.valueOf(amountBase + amountNoise).setScale(2, java.math.RoundingMode.HALF_UP);
        BigDecimal riskScore = switch (riskLevel) {
            case "HIGH" -> BigDecimal.valueOf(0.72 + random.nextDouble(0.23));
            case "MEDIUM" -> BigDecimal.valueOf(0.40 + random.nextDouble(0.25));
            default -> BigDecimal.valueOf(0.08 + random.nextDouble(0.22));
        };

        com.fasterxml.jackson.databind.node.ObjectNode riskFeatures = mapper.createObjectNode();
        riskFeatures.put("device_fingerprint", "fp_TXN" + String.format("%04d", seq));
        riskFeatures.put("ip_address", getIPPrefixByCountry(country) + "." + random.nextInt(10, 220) + "." + random.nextInt(1, 250));
        riskFeatures.put("user_behavior_score", calculateBehaviorScore(userLabel, deviceRisk));
        riskFeatures.put("transaction_velocity", random.nextInt(1, 7));
        riskFeatures.put("geolocation_mismatch", random.nextBoolean());
        riskFeatures.put("device_age_days", random.nextInt(1, 300));

        return RiskCase.builder()
                .bizTransactionId("TXN" + String.format("%04d", seq))
                .amount(amount)
                .currency(currency)
                .country(country)
                .deviceRisk(deviceRisk)
                .userLabel(userLabel)
                .riskLevel(riskLevel)
                .riskStatus(riskStatus)
                .riskScore(riskScore)
                .riskFeatures(riskFeatures)
                .build();
    }
    
    private String getIPPrefixByCountry(String country) {
        switch (country) {
            case "US": return "192.168";
            case "CN": return "10.0";
            case "RU": return "172.16";
            case "DE": return "203.0";
            case "GB": return "195.0";
            case "JP": return "210.0";
            case "IN": return "49.0";
            case "FR": return "80.0";
            case "BR": return "177.0";
            case "CA": return "99.0";
            default: return "192.0";
        }
    }
    
    private int calculateBehaviorScore(String userLabel, String deviceRisk) {
        int score = 50;  // Base score
        
        if ("new_user".equals(userLabel)) {
            score -= 20;  // New users have lower scores
        } else if ("vip_user".equals(userLabel)) {
            score += 20;  // VIP users have higher scores
        }
        
        if ("HIGH".equals(deviceRisk)) {
            score -= 15;
        } else if ("LOW".equals(deviceRisk)) {
            score += 10;
        }
        
        return Math.max(0, Math.min(100, score));
    }

    private void initializeAIDecisions() {
        log.info("Initializing AI decision records...");
        List<RiskCase> allCases = riskCaseRepository.findAll();
        if (allCases.isEmpty()) {
            log.info("No risk cases found, skipping AI decision initialization");
            return;
        }

        int decisionCaseCount = Math.min(TARGET_DECISION_CASE_COUNT, allCases.size());
        int created = 0;

        for (int i = 0; i < decisionCaseCount; i++) {
            RiskCase riskCase = allCases.get(i);
            Long caseId = riskCase.getId();

            if (!aiDecisionRecordRepository.existsByCaseIdAndPromptVersionAndDeletedAtIsNull(caseId, "v1")) {
                aiDecisionRecordRepository.save(buildSyntheticDecision(riskCase, "v1"));
                created++;
            }
            if (!aiDecisionRecordRepository.existsByCaseIdAndPromptVersionAndDeletedAtIsNull(caseId, "v2")) {
                aiDecisionRecordRepository.save(buildSyntheticDecision(riskCase, "v2"));
                created++;
            }
        }

        log.info("AI decision records initialized/backfilled: {} new records created", created);
    }

    private AIDecisionRecord buildSyntheticDecision(RiskCase riskCase, String promptVersion) {
        String riskLevel = riskCase.getRiskLevel() == null ? "MEDIUM" : riskCase.getRiskLevel();
        String suggestedAction = switch (riskLevel) {
            case "HIGH" -> "REJECT";
            case "LOW" -> "APPROVE";
            default -> "MANUAL_REVIEW";
        };
        BigDecimal baseConfidence = switch (riskLevel) {
            case "HIGH" -> BigDecimal.valueOf(0.84);
            case "LOW" -> BigDecimal.valueOf(0.90);
            default -> BigDecimal.valueOf(0.76);
        };
        if ("v2".equals(promptVersion)) {
            baseConfidence = baseConfidence.add(BigDecimal.valueOf(0.04));
        }
        int totalMs = "v2".equals(promptVersion)
                ? ThreadLocalRandom.current().nextInt(850, 1250)
                : ThreadLocalRandom.current().nextInt(1050, 1650);

        String reasoning = switch (riskLevel) {
            case "HIGH" -> "检测到高风险信号组合，建议优先拦截并进行人工复核。";
            case "LOW" -> "交易行为与历史模式一致，整体风险较低。";
            default -> "风险信号存在不确定性，建议进入人工复核流程。";
        };

        return AIDecisionRecord.builder()
                .caseId(riskCase.getId())
                .promptVersion(promptVersion)
                .suggestedAction(suggestedAction)
                .confidenceScore(baseConfidence)
                .totalTimeMs(totalMs)
                .riskLevel(riskLevel)
                .reasoning(reasoning)
                .keyRiskPoints("金额模式, 设备风险, 用户标签")
                .similarCasesAnalysis("已匹配历史相似案例并完成对比分析。")
                .ruleEngineAlignment("已结合规则分进行一致性校验。")
                .build();
    }
}
