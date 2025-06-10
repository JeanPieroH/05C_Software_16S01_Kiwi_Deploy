const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

//--------------------------
exports.create = async ({ name, description, teachers}) => {
  return prisma.classroom.create({
    data: {
      name,
      description,
      total_points: 0,
      teachers: {
        create: teachers.map(t => ({ id_teacher: t , role_classroom: "OWNER"}))
      },
    },
    include: { teachers: true, students: true, competences: true }
  });
};
//--------------------------
exports.addMultipleStudentsToClassroom = async (studentsToAdd) => {
  const result = await prisma.Classroom_Student.createMany({ data: studentsToAdd, skipDuplicates: true });
  return result;
};

exports.isStudentInClassroom = async (id_student, id_classroom) => {
  const existingEntry = await prisma.Classroom_Student.findUnique({
    where: { id_student_id_classroom: { id_student, id_classroom } },
  });
  return !!existingEntry;
};

exports.findClassroomById = async (id) => {
  return await prisma.Classroom.findUnique({ where: { id } });
};
//--------------------------
exports.addMultipleTeachersToClassroom = async (teachersToAdd) => {
  const result = await prisma.Classroom_Teacher.createMany({ data: teachersToAdd, skipDuplicates: true });
  return result;
};

exports.isTeacherInClassroom = async (id_teacher, id_classroom) => {
  const existingEntry = await prisma.Classroom_Teacher.findUnique({
    where: { id_classroom_id_teacher: { id_teacher, id_classroom } },
  });
  return !!existingEntry;
};
//-----------------

exports.findTeachersByClassroomId = async (classroomId) => {
  const classroomTeachers = await prisma.Classroom_Teacher.findMany({
    where: { id_classroom: classroomId },
    select: { id_teacher: true },
  });
  return classroomTeachers.map(ct => ct.id_teacher);
};

exports.findStudentsByClassroomId = async (classroomId) => {
  const classroomStudents = await prisma.Classroom_Student.findMany({
    where: { id_classroom: classroomId },
    select: { id_student: true },
  });
  return classroomStudents.map(cs => cs.id_student);
};
//----------------------------
exports.findClassroomsByTeacherId = async (teacherId) => {
  return await prisma.Classroom_Teacher.findMany({
    where: { id_teacher: teacherId },
    select: {
      classroom: {
        select: {
          id: true,
          name: true,
          description: true,
        },
      },
    },
  });
};

exports.findClassroomsByStudentId = async (studentId) => {
  return await prisma.Classroom_Student.findMany({
    where: { id_student: studentId },
    select: {
      classroom: {
        select: {
          id: true,
          name: true,
          description: true,
        },
      },
    },
  });
};
//----------------
exports.update = async (id, { name, description, teachers, students, competences }) => {
  return prisma.classroom.update({
    where: { id },
    data: {
      name,
      description,
      teachers: {
        create: teachers?.map(t => ({ id_teacher: t }))
      },
      students: {
        create: students?.map(s => ({ id_student: s }))
      },
      competences: {
        create: competences?.map(c => ({
          id_student: c.studentId,
          id_competence: c.competenceId,
          obtained_points: c.obtained_points || 0,
          total_points: c.total_points || 0
        }))
      }
    },
    include: { teachers: true, students: true, competences: true }
  });
};

  
// ------------
exports.findById = async (id) => {
  return await prisma.classroom.findUnique({
    where: { id },
    select: {
      id: true,
      name: true,
      description: true,
      quiz: true,
      competences: {
        select: {
          competence: { // Esto es lo que nos dará el objeto { id, name, description }
            select: {
              id: true,
              name: true,
              description: true
            }
          }
        }
      }
    }
  });
};


exports.findByTeacherId = async (id_teacher) => {
  return prisma.classroom.findMany({
    where: {
      teachers: {
        some: {
          id_teacher: id_teacher
        }
      }
    },
    select: {
      id: true,
      name: true,
      description: true,
    }
  });
};

// -------------------


exports.findAll = async () => {
    return prisma.classroom.findMany({
        include: {
        teachers: true,
        students: true,
        competences: true
        }
    });
};


exports.getCompetencesByClassroomId = async (classroomId) => {
  const classroom = await prisma.classroom.findUnique({
    where: { id: classroomId },
    include: {
      // Incluimos la tabla de unión Classroom_Competence_Student
      competences: {
        // Dentro de la tabla de unión, seleccionamos los detalles de la Competence
        select: {
          competence: {
            select: {
              id: true,
              name: true,
              description: true,
              id_teacher: true,
              // Agrega aquí cualquier otro campo de Competence que necesites
            }
          }
        }
      }
    }
  });

  if (!classroom) {
    return null; // El Classroom no fue encontrado
  }

  // Mapeamos el resultado para obtener solo los objetos de Competence
  // El resultado de Prisma es [{ competence: {...} }, { competence: {...} }]
  // Lo transformamos a [{...}, {...}]
  return classroom.competences.map(cc => cc.competence);
};

// --------------------------
exports.addMultipleCompetencesToClassroom = async (data) => {
  const result = await prisma.Classroom_Competence.createMany({ data, skipDuplicates: true });
  return result;
};

exports.isCompetenceInClassroom = async (id_competence, id_classroom) => {
  const existingEntry = await prisma.Classroom_Competence.findUnique({
    where: { id_classroom_id_competence: { id_competence, id_classroom } },
  });
  return !!existingEntry;
};

exports.findCompetencesByIds = async (ids) => {
  return await prisma.Competence.findMany({ where: { id: { in: ids } } });
};
// -------------------------------------

exports.updateQuizListAndTotalPoints = async (id, newQuizIds, pointsToAdd) => {
  return await prisma.classroom.update({
    where: { id },
    data: { 
      quiz: { set: newQuizIds },
      total_points: { increment: pointsToAdd } 
    },
  });
};

//------------------------------------

exports.upsertStudentPoints = async (id_student, id_classroom, obtained_points) => {
  return await prisma.Classroom_Student.update({
    where: {
      id_student_id_classroom: { id_student, id_classroom },
    },
    data: { obtained_points: { increment: obtained_points } }
  });
};

//---------------------------------


exports.findStudentsByClassroomIdOrderedByPoints = async (classroomId) => {
  return await prisma.Classroom_Student.findMany({
    where: { id_classroom: classroomId },
    orderBy: { obtained_points: 'desc' },
    select: {
      id_student: true,
      obtained_points: true,
    },
  });
};


exports.findStudentsByClassroomAndCompetenceIdOrderedByPoints = async (classroomId, competenceId) => {
  return await prisma.Classroom_Competence_Student.findMany({
    where: {
      id_classroom: classroomId,
      id_competence: competenceId,
    },
    orderBy: { obtained_points: 'desc' },
    select: {
      id_student: true,
      obtained_points: true,
    },
  });
};