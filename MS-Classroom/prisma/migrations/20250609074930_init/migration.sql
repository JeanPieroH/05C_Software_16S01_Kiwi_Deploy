-- CreateTable
CREATE TABLE "Classroom" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "total_points" INTEGER NOT NULL,
    "quiz" INTEGER[],

    CONSTRAINT "Classroom_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Classroom_Teacher" (
    "id_classroom" INTEGER NOT NULL,
    "id_teacher" INTEGER NOT NULL,
    "role_classroom" TEXT NOT NULL,

    CONSTRAINT "Classroom_Teacher_pkey" PRIMARY KEY ("id_classroom","id_teacher")
);

-- CreateTable
CREATE TABLE "Classroom_Student" (
    "id_student" INTEGER NOT NULL,
    "id_classroom" INTEGER NOT NULL,
    "role_classroom" TEXT NOT NULL,
    "obtained_points" INTEGER NOT NULL,

    CONSTRAINT "Classroom_Student_pkey" PRIMARY KEY ("id_student","id_classroom")
);

-- CreateTable
CREATE TABLE "Competence" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "id_teacher" INTEGER NOT NULL,

    CONSTRAINT "Competence_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Classroom_Competence" (
    "id_classroom" INTEGER NOT NULL,
    "id_competence" INTEGER NOT NULL,
    "total_points" INTEGER NOT NULL,

    CONSTRAINT "Classroom_Competence_pkey" PRIMARY KEY ("id_classroom","id_competence")
);

-- CreateTable
CREATE TABLE "Competence_Question" (
    "id_competence" INTEGER NOT NULL,
    "id_question" INTEGER NOT NULL,

    CONSTRAINT "Competence_Question_pkey" PRIMARY KEY ("id_competence","id_question")
);

-- CreateTable
CREATE TABLE "Classroom_Competence_Student" (
    "id_student" INTEGER NOT NULL,
    "id_competence" INTEGER NOT NULL,
    "id_classroom" INTEGER NOT NULL,
    "obtained_points" INTEGER NOT NULL,

    CONSTRAINT "Classroom_Competence_Student_pkey" PRIMARY KEY ("id_student","id_competence","id_classroom")
);

-- AddForeignKey
ALTER TABLE "Classroom_Teacher" ADD CONSTRAINT "Classroom_Teacher_id_classroom_fkey" FOREIGN KEY ("id_classroom") REFERENCES "Classroom"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Classroom_Student" ADD CONSTRAINT "Classroom_Student_id_classroom_fkey" FOREIGN KEY ("id_classroom") REFERENCES "Classroom"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Classroom_Competence" ADD CONSTRAINT "Classroom_Competence_id_classroom_fkey" FOREIGN KEY ("id_classroom") REFERENCES "Classroom"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Classroom_Competence" ADD CONSTRAINT "Classroom_Competence_id_competence_fkey" FOREIGN KEY ("id_competence") REFERENCES "Competence"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Competence_Question" ADD CONSTRAINT "Competence_Question_id_competence_fkey" FOREIGN KEY ("id_competence") REFERENCES "Competence"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Classroom_Competence_Student" ADD CONSTRAINT "Classroom_Competence_Student_id_competence_fkey" FOREIGN KEY ("id_competence") REFERENCES "Competence"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Classroom_Competence_Student" ADD CONSTRAINT "Classroom_Competence_Student_id_classroom_fkey" FOREIGN KEY ("id_classroom") REFERENCES "Classroom"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
