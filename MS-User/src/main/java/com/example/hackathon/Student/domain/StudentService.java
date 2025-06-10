package com.example.hackathon.Student.domain;


import java.security.Principal;

import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.hackathon.Exceptions.NotFoundException;
import com.example.hackathon.Student.dto.RpStudentId;
import com.example.hackathon.Student.infrastructure.StudentRepository;
import com.example.hackathon.Usuario.dto.RqListEmail;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class StudentService{
    @Autowired
    StudentRepository studentRepository;
    @Autowired
    ModelMapper modelMapper;

    public Student getStudent(Principal principal){
        Student student=studentRepository.findByEmail(principal.getName()).orElseThrow(() -> new NotFoundException("Student not found"));
        System.out.println(student);
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

    public List<Student> getStudentsByIds(List<Long> studentIds) {
        return studentRepository.findAllById(studentIds);
    }

    public RpStudentId getStudentsIdsbyEmail(RqListEmail emails) {
        List<Student> students = studentRepository.findByEmailIn(emails.getEmails());
        List<Long> studentIds = students.stream().map(Student::getId).collect(Collectors.toList());

        RpStudentId response = new RpStudentId();
        response.setStudents_id(studentIds);
        return response;
    }

    public Student addPoints(Long id_student, int points){
        Student student=studentRepository.findById(id_student).orElseThrow(() -> new NotFoundException("Student not found"));
        student.setCoinEarned(student.getCoinEarned()+points);
        student.setCoinAvailable(student.getCoinAvailable()+points);

        studentRepository.save(student);
        return student;
    }

} 