package com.riskcontrol.service;

import com.riskcontrol.entity.User;
import com.riskcontrol.repository.UserRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    @InjectMocks
    private UserService userService;

    @AfterEach
    void tearDown() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void deleteUser_shouldRejectSelfDeletion() {
        User self = User.builder()
            .id(1L)
            .username("admin")
            .build();
        when(userRepository.findById(1L)).thenReturn(Optional.of(self));

        SecurityContextHolder.getContext().setAuthentication(
            new UsernamePasswordAuthenticationToken("admin", "N/A")
        );

        assertThrows(IllegalArgumentException.class, () -> userService.deleteUser(1L));
    }

    @Test
    void deactivateUser_shouldRejectSelfDeactivation() {
        User self = User.builder()
            .id(1L)
            .username("admin")
            .status("ACTIVE")
            .build();
        when(userRepository.findById(1L)).thenReturn(Optional.of(self));

        SecurityContextHolder.getContext().setAuthentication(
            new UsernamePasswordAuthenticationToken("admin", "N/A")
        );

        assertThrows(IllegalArgumentException.class, () -> userService.deactivateUser(1L));
    }
}
