package com.example.hackathon.Student.domain;

import com.example.hackathon.Usuario.domain.Usuario;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;


@Entity(name ="Student")

public class Student extends Usuario{
    @Column
    @Enumerated(EnumType.STRING)
    private Emotional emotion; 
    
}
