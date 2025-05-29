package com.example.hackathon.Auth.dto;


import jakarta.validation.constraints.Email;
import lombok.Data;

@Data
public class RqUserLoginDto {

    @Email
    String email;
    String password;
}
