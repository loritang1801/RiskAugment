package com.riskcontrol.controller;

import com.riskcontrol.dto.LoginRequest;
import com.riskcontrol.dto.LoginResponse;
import com.riskcontrol.entity.User;
import com.riskcontrol.repository.UserRepository;
import com.riskcontrol.service.JwtService;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.Optional;

@Slf4j
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = {"http://localhost:3000", "http://localhost:3001", "http://localhost:5173"})
public class AuthController {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        log.info("Login attempt for user: {}", request.getUsername());

        try {
            Optional<User> userOpt = userRepository.findByUsername(request.getUsername());
            if (userOpt.isEmpty()) {
                return ResponseEntity.status(401).body(Map.of(
                    "status", "error",
                    "message", "Invalid username or password"
                ));
            }

            User user = userOpt.get();
            if (!"ACTIVE".equals(user.getStatus())) {
                return ResponseEntity.status(401).body(Map.of(
                    "status", "error",
                    "message", "User is not active"
                ));
            }

            if (request.getPassword() == null
                || request.getPassword().isEmpty()
                || !passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
                return ResponseEntity.status(401).body(Map.of(
                    "status", "error",
                    "message", "Invalid username or password"
                ));
            }

            String token = jwtService.generateToken(user.getUsername(), user.getRole());
            user.setLastLoginAt(LocalDateTime.now());
            userRepository.save(user);

            LoginResponse response = LoginResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .expiresInHours(jwtService.getExpirationHours())
                .username(user.getUsername())
                .fullName(user.getFullName())
                .role(user.getRole())
                .build();

            return ResponseEntity.ok(Map.of(
                "status", "success",
                "data", response
            ));
        } catch (Exception e) {
            log.error("Login error", e);
            return ResponseEntity.status(500).body(Map.of(
                "status", "error",
                "message", "Login failed"
            ));
        }
    }

    @GetMapping("/validate")
    public ResponseEntity<?> validateToken(@RequestHeader(value = "Authorization", required = false) String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return ResponseEntity.status(401).body(Map.of(
                "status", "error",
                "message", "Invalid token"
            ));
        }

        String token = authHeader.substring(7);
        if (!jwtService.isTokenValid(token)) {
            return ResponseEntity.status(401).body(Map.of(
                "status", "error",
                "message", "Token is invalid or expired"
            ));
        }

        Claims claims = jwtService.parseClaims(token);
        return ResponseEntity.ok(Map.of(
            "status", "success",
            "data", Map.of(
                "username", claims.getSubject(),
                "role", claims.get("role", String.class)
            )
        ));
    }
}
