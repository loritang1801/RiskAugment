package com.riskcontrol.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateUserRequest {

    @NotBlank(message = "Full name is required")
    @Size(max = 100, message = "Full name must not exceed 100 characters")
    private String fullName;

    @NotBlank(message = "Role is required")
    @Pattern(regexp = "^(ADMIN|REVIEWER|ANALYST)$", message = "Role must be one of ADMIN, REVIEWER, ANALYST")
    private String role;  // ADMIN, REVIEWER, ANALYST

    private String department;

    @Pattern(
        regexp = "^(ACTIVE|INACTIVE|LOCKED)$",
        message = "Status must be one of ACTIVE, INACTIVE, LOCKED"
    )
    private String status;  // ACTIVE, INACTIVE, LOCKED
}
