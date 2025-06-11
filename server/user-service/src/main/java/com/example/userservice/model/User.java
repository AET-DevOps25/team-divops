package com.example.userservice.model;

import jakarta.persistence.*;
import lombok.Getter;
import org.hibernate.annotations.UuidGenerator;

import java.time.LocalDate;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue
    @UuidGenerator
    @Column(updatable = false, nullable = false)
    private String id;

    @Getter
    @Column(name = "email", nullable = false, unique = true)
    String email;

    @Getter
    @Column(name = "first_name", nullable = false)
    String firstName;

    @Getter
    @Column(name = "last_name", nullable = false)
    String lastName;

    @Getter
    @Column(name = "birthdate", nullable = false)
    LocalDate birthdate;

    @Getter
    @Column(name = "password", nullable = false)
    String password;

    @Getter
    @Column(name = "role", nullable = false, columnDefinition = "VARCHAR(255) DEFAULT 'USER'")
    String role = "USER";

    @Getter
    @Column(name = "enabled", nullable = false, columnDefinition = "BOOLEAN DEFAULT TRUE")
    boolean enabled = true;

    protected User() {
        // no-args constructor required by JPA spec
        // this one is protected since it shouldn’t be used directly
    }

    public User(String email, String firstName, String lastName, LocalDate birthdate, String password, String role, boolean enabled) {
        this.email = email;
        this.firstName = firstName;
        this.lastName = lastName;
        this.birthdate = birthdate;
        this.password = password;
        this.role = role;
        this.enabled = enabled;
    }
}
