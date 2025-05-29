package com.example.hackathon.Auth.dto;

import com.example.hackathon.Usuario.domain.Role;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.Date;

@Data
public class RqUserRegisterDto {
    String name;
    String last_name;
    @Email
    @NotNull
    private String email;
    @NotNull
    @Size(min = 8, max = 16)
    private String password;
    private Role role;
    private Date registration_date;
    private String cel_phone;

}
