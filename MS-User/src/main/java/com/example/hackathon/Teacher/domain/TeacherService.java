package com.example.hackathon.Teacher.domain;

import java.security.Principal;
import java.util.List;
import java.util.stream.Collectors;

import org.modelmapper.ModelMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.hackathon.Exceptions.NotFoundException;
import com.example.hackathon.Student.domain.Student;
import com.example.hackathon.Student.dto.RpStudentId;
import com.example.hackathon.Teacher.dto.RpTeacherId;
import com.example.hackathon.Teacher.infrastructure.TeacherRepository;
import com.example.hackathon.Usuario.dto.RqListEmail;

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

    public List<Teacher> getTeachersByIds(List<Long> teacherIds) {
        return teacherRepository.findAllById(teacherIds);
    }

    public RpTeacherId getTeachersIdsbyEmail(RqListEmail emails) {
        List<Teacher> teachers = teacherRepository.findByEmailIn(emails.getEmails());
        // Extraer solo los IDs
        List<Long> TeacherIds = teachers.stream().map(Teacher::getId).collect(Collectors.toList());

        RpTeacherId response = new RpTeacherId();
        response.setTeachers_id(TeacherIds);
        return response;
    }
}
