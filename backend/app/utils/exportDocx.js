import {
  Document,
  Packer,
  Paragraph,
  TextRun,
} from "docx";

import { saveAs } from "file-saver";

export async function exportResumeToDocx(markdown) {
  const lines = markdown.split("\n");

  const paragraphs = lines.map((line) => {
    if (line.startsWith("# ")) {
      return new Paragraph({
        heading: "Heading1",
        children: [
          new TextRun({
            text: line.replace("# ", ""),
            bold: true,
            size: 34,
          }),
        ],
      });
    }

    if (line.startsWith("## ")) {
      return new Paragraph({
        heading: "Heading2",
        children: [
          new TextRun({
            text: line.replace("## ", ""),
            bold: true,
            size: 28,
          }),
        ],
      });
    }

    if (line.startsWith("- ")) {
      return new Paragraph({
        bullet: {
          level: 0,
        },
        children: [
          new TextRun(
            line.replace("- ", "")
          ),
        ],
      });
    }

    return new Paragraph({
      children: [
        new TextRun(line),
      ],
    });
  });

  const doc = new Document({
    sections: [
      {
        children: paragraphs,
      },
    ],
  });

  const blob = await Packer.toBlob(doc);

  saveAs(blob, "Improved_Resume.docx");
}