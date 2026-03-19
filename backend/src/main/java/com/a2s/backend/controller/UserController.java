package com.a2s.backend.controller;

import com.a2s.backend.repository.UserRepository;
import com.a2s.backend.security.services.UserDetailsImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    UserRepository userRepository;

    @GetMapping("/profile")
    public ResponseEntity<?> getUserProfile() {
        UserDetailsImpl userDetails = (UserDetailsImpl) SecurityContextHolder.getContext().getAuthentication()
                .getPrincipal();

        return userRepository.findById(userDetails.getId())
                .map(user -> ResponseEntity.ok(user))
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PutMapping("/profile")
    public ResponseEntity<?> updateUserProfile(@RequestBody Map<String, Object> updates) {
        UserDetailsImpl userDetails = (UserDetailsImpl) SecurityContextHolder.getContext().getAuthentication()
                .getPrincipal();

        return userRepository.findById(userDetails.getId())
                .map(user -> {
                    if (updates.containsKey("name"))
                        user.setName((String) updates.get("name"));
                    if (updates.containsKey("location"))
                        user.setLocation((String) updates.get("location"));
                    // Password update should be handled separately with encryption, skipping for
                    // now as per api.js needs
                    userRepository.save(user);
                    return ResponseEntity.ok(user);
                })
                .orElseGet(() -> ResponseEntity.notFound().build());
    }

    @PostMapping("/saved-designs")
    public ResponseEntity<?> toggleSavedDesign(@RequestBody Map<String, String> payload) {
        String designId = payload.get("designId");
        UserDetailsImpl userDetails = (UserDetailsImpl) SecurityContextHolder.getContext().getAuthentication()
                .getPrincipal();

        return userRepository.findById(userDetails.getId())
                .map(user -> {
                    List<String> saved = user.getSavedDesigns();
                    if (saved == null)
                        saved = new ArrayList<>();

                    if (saved.contains(designId)) {
                        saved.remove(designId);
                    } else {
                        saved.add(designId);
                    }
                    user.setSavedDesigns(saved);
                    userRepository.save(user);
                    return ResponseEntity.ok(saved);
                })
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}
