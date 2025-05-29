package com.example.hackathon.Student.domain;


import java.security.Principal;

import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.hackathon.Exceptions.NotFoundException;
import com.example.hackathon.Student.infrastructure.StudentRepository;

@Service
public class StudentService{
    @Autowired
    StudentRepository studentRepository;
    @Autowired
    ModelMapper modelMapper;

    public Student getStudent(Principal principal){
        Student student=studentRepository.findByEmail(principal.getName()).orElseThrow(() -> new NotFoundException("Student not found"));
        return student;
    }

    public Student patchStudent(Principal principal,Student new_student){
        Student student=studentRepository.findByEmail(principal.getName()).orElseThrow(() -> new NotFoundException("Student not found"));
        modelMapper.map(new_student,student);

        studentRepository.save(student);
        return student;
    }

    public Student getallStudent(Principal principal,Student new_student){
        Student student=studentRepository.findByEmail(principal.getName()).orElseThrow(() -> new NotFoundException("Student not found"));
        modelMapper.map(new_student,student);

        studentRepository.save(student);
        return student;
    }

} 