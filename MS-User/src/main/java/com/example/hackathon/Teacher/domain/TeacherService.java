package com.example.hackathon.Teacher.domain;

import java.security.Principal;

import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.hackathon.Exceptions.NotFoundException;
import com.example.hackathon.Teacher.infrastructure.TeacherRepository;

@Service
public class TeacherService {
    
    @Autowired
    TeacherRepository teacherRepository;
    @Autowired
    ModelMapper modelMapper;

    public Teacher getTeacher(Principal principal){
        Teacher teacher=teacherRepository.findByEmail(principal.getName()).orElseThrow(() -> new NotFoundException("Student not found"));
        return teacher;
    }

    public Teacher patchTeacher(Principal principal,Teacher new_teacher){
        Teacher teacher=teacherRepository.findByEmail(principal.getName()).orElseThrow(() -> new NotFoundException("Student not found"));
        modelMapper.map(new_teacher,teacher);

        teacherRepository.save(teacher);
        return teacher;
    }
}
