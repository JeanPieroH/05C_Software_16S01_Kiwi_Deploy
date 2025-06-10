const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

exports.create = ({ name, description, id_teacher }) => {
  return prisma.competence.create({
    data: { name, description, id_teacher }
  });
};
exports.findAll = () => {
    return prisma.competence.findMany({
      include:{
        questions : true,
        classroom_student : true,
        classroom :true
      }
    }
    );
  };
  
exports.findById = (id) => {
  return prisma.competence.findUnique({
    where: { id }
  });
};

exports.findByTeacherId = (id_teacher) => {
return prisma.competence.findMany({
  where: { id_teacher: id_teacher },
  select: {
      id: true,
      name: true,
      description: true,
    },
});
};

exports.findCompetencesByClassroomId = async (classroomId) => {
  return await prisma.Classroom_Competence.findMany({
    where: { id_classroom: classroomId },
    select: {
      competence: {
        select: {
          id: true,
          name: true,
          description: true,
        },
      },
    },
  });
};

// -----------------------------------
exports.addMultipleCompetenceQuestions = async (data) => {
  const result = await prisma.Competence_Question.createMany({
    data: data,
    skipDuplicates: true,
  });
  return result;
};

exports.findCompetencesByIds = async (ids) => {
  return await prisma.competence.findMany({ where: { id: { in: ids } } });
};

exports.upsertTotalPoints = async (id_classroom, id_competence, pointsToAdd) => {
  return await prisma.classroom_Competence.upsert({
    where: { id_classroom_id_competence: { id_classroom, id_competence } },
    update: { total_points: { increment: pointsToAdd } },
    create: { id_classroom, id_competence, total_points: pointsToAdd },
  });
};
exports.findCompetenceById = async (id) => {
  return await prisma.Competence.findUnique({ where: { id } });
};
//-------------------------

exports.findCompetenceIdsByQuestionId = async (questionId) => {
  const associations = await prisma.competence_Question.findMany({
    where: { id_question: questionId },
    select: { id_competence: true },
  });
  return associations.map((a) => a.id_competence);
};

exports.findCompetencesByIds = async (ids) => {
  return await prisma.Competence.findMany({ where: { id: { in: ids } } });
};

exports.upsertStudentCompetencePoints = async (
  id_student,
  id_competence,
  id_classroom,
  obtained_points
) => {
  return await prisma.Classroom_Competence_Student.upsert({
    where: {
      id_student_id_competence_id_classroom: {
        id_student,
        id_competence,
        id_classroom,
      },
    },
    update: { obtained_points: { increment: obtained_points } },
    create: {
      id_student,
      id_competence,
      id_classroom,
      obtained_points: obtained_points,
    },
  });
};

exports.findStudentInClassroom = async (id_student, id_classroom) => {
  return await prisma.Classroom_Student.findUnique({
    where: { id_student_id_classroom: { id_student, id_classroom } },
  });
};

//----------------------