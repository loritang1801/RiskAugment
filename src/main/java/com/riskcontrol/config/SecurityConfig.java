package com.riskcontrol.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.util.matcher.AntPathRequestMatcher;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    
    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // Disable CSRF
            .csrf().disable()
            // Enable CORS
            .cors().and()
            // Disable basic authentication
            .httpBasic().disable()
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            // Configure authorization
            .authorizeHttpRequests(authz -> authz
                // Public auth endpoints
                .requestMatchers(new AntPathRequestMatcher("/api/auth/login")).permitAll()
                .requestMatchers(new AntPathRequestMatcher("/api/auth/validate")).authenticated()
                // Health endpoints
                .requestMatchers(new AntPathRequestMatcher("/health")).permitAll()
                // Allow public access to Swagger/OpenAPI
                .requestMatchers(new AntPathRequestMatcher("/swagger-ui/**")).permitAll()
                .requestMatchers(new AntPathRequestMatcher("/v3/api-docs/**")).permitAll()
                .requestMatchers(new AntPathRequestMatcher("/swagger-ui.html")).permitAll()
                // Allow public access to H2 console
                .requestMatchers(new AntPathRequestMatcher("/h2-console/**")).permitAll()
                // Role-based authorization
                .requestMatchers(new AntPathRequestMatcher("/api/users/**")).hasRole("ADMIN")
                .requestMatchers(new AntPathRequestMatcher("/api/prompts/**")).hasRole("ADMIN")
                .requestMatchers(new AntPathRequestMatcher("/api/analytics/**")).hasAnyRole("ADMIN", "REVIEWER", "ANALYST")
                .requestMatchers(new AntPathRequestMatcher("/api/cases/**")).hasAnyRole("ADMIN", "REVIEWER", "ANALYST")
                .requestMatchers(new AntPathRequestMatcher("/api/ai-decisions/**")).hasAnyRole("ADMIN", "REVIEWER", "ANALYST")
                .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                // All other requests require authentication
                .anyRequest().authenticated()
            )
            // Disable frame options for H2 console
            .headers(headers -> headers.frameOptions().disable())
            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
        
        return http.build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(Arrays.asList(
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:5173"
        ));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        configuration.setMaxAge(3600L);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
