package com.a2s.backend.controller;

import com.a2s.backend.model.User;
import com.a2s.backend.repository.UserRepository;
import com.a2s.backend.security.jwt.JwtUtils;
import com.a2s.backend.security.services.UserDetailsImpl;
import jakarta.validation.Valid;
import lombok.Data;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/users")
public class AuthController {
    @Autowired
    AuthenticationManager authenticationManager;

    @Autowired
    UserRepository userRepository;

    @Autowired
    PasswordEncoder encoder;

    @Autowired
    JwtUtils jwtUtils;

    @PostMapping("/login")
    public ResponseEntity<?> authenticateUser(@Valid @RequestBody LoginRequest loginRequest) {
        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(loginRequest.getEmail(), loginRequest.getPassword()));

        SecurityContextHolder.getContext().setAuthentication(authentication);
        String jwt = jwtUtils.generateJwtToken(authentication);

        UserDetailsImpl userDetails = (UserDetailsImpl) authentication.getPrincipal();

        return ResponseEntity.ok(new JwtResponse(jwt,
                userDetails.getId(),
                userDetails.getUsername(),
                userDetails.getName(),
                userDetails.getLocation()));
    }

    @PostMapping("/register")
    public ResponseEntity<?> registerUser(@Valid @RequestBody SignupRequest signUpRequest) {
        if (userRepository.existsByEmail(signUpRequest.getEmail())) {
            return ResponseEntity
                    .badRequest()
                    .body(new MessageResponse("Error: Email is already in use!"));
        }

        // Create new user's account
        User user = new User();
        user.setName(signUpRequest.getName());
        user.setEmail(signUpRequest.getEmail());
        user.setPassword(encoder.encode(signUpRequest.getPassword()));
        user.setLocation(signUpRequest.getLocation());
        user.setMemberSince(LocalDate.now().toString());

        userRepository.save(user);

        return ResponseEntity.ok(new MessageResponse("User registered successfully!"));
    }

    @PostMapping("/forgot-password")
    public ResponseEntity<?> forgotPassword(@Valid @RequestBody ForgotPasswordRequest request) {
        Optional<User> userOptional = userRepository.findByEmail(request.getEmail());
        if (userOptional.isPresent()) {
            User user = userOptional.get();
            String token = UUID.randomUUID().toString();
            user.setResetPasswordToken(token);
            user.setResetPasswordExpiry(LocalDateTime.now().plusHours(1));
            userRepository.save(user);

            // Simulation of email sending
            System.out.println("==================================================");
            System.out.println("PASSWORD RESET REQUEST FOR: " + user.getEmail());
            System.out.println("RESET TOKEN: " + token);
            System.out.println("LINK: http://localhost:5173/reset-password?token=" + token);
            System.out.println("==================================================");

            return ResponseEntity
                    .ok(new MessageResponse("If your email is registered, you will receive a reset link shortly."));
        }

        // Anti-enumeration: always return the same message
        return ResponseEntity
                .ok(new MessageResponse("If your email is registered, you will receive a reset link shortly."));
    }

    @PostMapping("/reset-password")
    public ResponseEntity<?> resetPassword(@Valid @RequestBody ResetPasswordRequest request) {
        Optional<User> userOptional = userRepository.findByResetPasswordToken(request.getToken());

        if (userOptional.isPresent()) {
            User user = userOptional.get();
            if (user.getResetPasswordExpiry().isAfter(LocalDateTime.now())) {
                user.setPassword(encoder.encode(request.getNewPassword()));
                user.setResetPasswordToken(null);
                user.setResetPasswordExpiry(null);
                userRepository.save(user);
                return ResponseEntity.ok(new MessageResponse("Password reset successful!"));
            } else {
                return ResponseEntity.badRequest().body(new MessageResponse("Error: Token has expired!"));
            }
        }

        return ResponseEntity.badRequest().body(new MessageResponse("Error: Invalid token!"));
    }

    // DTOs
    @Data
    public static class LoginRequest {
        private String email;
        private String password;
    }

    @Data
    public static class SignupRequest {
        @jakarta.validation.constraints.NotBlank
        private String name;
        @jakarta.validation.constraints.NotBlank
        @jakarta.validation.constraints.Email
        private String email;
        @jakarta.validation.constraints.NotBlank
        private String password;
        private String location;
    }

    @Data
    public static class ForgotPasswordRequest {
        @jakarta.validation.constraints.NotBlank
        @jakarta.validation.constraints.Email
        private String email;
    }

    @Data
    public static class ResetPasswordRequest {
        @jakarta.validation.constraints.NotBlank
        private String token;
        @jakarta.validation.constraints.NotBlank
        private String newPassword;
    }

    @Data
    public static class JwtResponse {
        private String token;
        private String type = "Bearer";
        private String id;
        private String email;
        private String name;
        private String location;

        public JwtResponse(String accessToken, String id, String email, String name, String location) {
            this.token = accessToken;
            this.id = id;
            this.email = email;
            this.name = name;
            this.location = location;
        }
    }

    @Data
    public static class MessageResponse {
        private String message;

        public MessageResponse(String message) {
            this.message = message;
        }
    }
}
