package com.a2s.backend.model;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import jakarta.persistence.*;
import com.fasterxml.jackson.annotation.JsonIgnore;

import java.time.LocalDateTime;
import java.util.List;
import java.util.ArrayList;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    private String name;

    @Column(unique = true)
    private String email;

    @JsonIgnore
    private String password;

    private String resetPasswordToken;
    private LocalDateTime resetPasswordExpiry;

    private String location;
    private String memberSince;

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "user_saved_designs", joinColumns = @JoinColumn(name = "user_id"))
    @Column(name = "design_id")
    private List<String> savedDesigns = new ArrayList<>();
}
