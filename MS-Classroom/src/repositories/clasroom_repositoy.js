const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

exports.create = async ({ name, description, teachers, students, competences }) => {
  return prisma.classroom.create({
    data: {
      name,
      description,
      teachers: {
        create: teachers.map(t => ({ id_teacher: t }))
      },
      students: {
        create: students.map(s => ({ id_student: s, coin_earned: 0, coin_available: 0 }))
      },
      competences: {
        create: competences.map(c => ({
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
        create: students?.map(s => ({ id_student: s, coin_earned: 0, coin_available: 0 }))
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

exports.findAll = async () => {
    return prisma.classroom.findMany({
        include: {
        teachers: true,
        students: true,
        competences: true
        }
    });
};
  
exports.findById = async (id) => {
    return prisma.classroom.findUnique({
      where: { id },
      include: {
        teachers: true,
        students: true,
        competences: true
      }
    });
};
  