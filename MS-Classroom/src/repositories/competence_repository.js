const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

exports.create = ({ name, description, id_teacher }) => {
  return prisma.competence.create({
    data: { name, description, id_teacher }
  });
};
exports.findAll = () => {
    return prisma.competence.findMany();
  };
  
  exports.findById = (id) => {
    return prisma.competence.findUnique({
      where: { id }
    });
  };
  