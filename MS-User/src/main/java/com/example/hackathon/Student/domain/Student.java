package com.example.hackathon.Student.domain;

import com.example.hackathon.Usuario.domain.Usuario;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import lombok.Data;

@Data
@Entity(name ="Student")
public class Student extends Usuario{
    @Column
    @Enumerated(EnumType.STRING)
    private Emotional emotion; 

    @Column(name = "coin_earned")
    private int coin_earned;

    @Column(name = "coin_available")
    private int coin_available;
}
