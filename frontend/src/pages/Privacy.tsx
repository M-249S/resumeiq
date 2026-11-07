import { LegalLayout, LegalSection } from "@/components/legal/LegalLayout";

export function Privacy() {
  return (
    <LegalLayout title="Privacy Policy" updated="7 November 2026">
      <p className="leading-relaxed text-ink-muted">
        ResumeIQ is a beta project built and run by Mujahid Adam. This page
        explains, in plain language, what data the app handles and why.
      </p>

      <LegalSection heading="What we collect">
        <ul className="list-disc space-y-1.5 pl-5">
          <li>
            <strong className="font-medium text-ink">Account details:</strong> your
            name and email address. If you sign up with a password it is stored
            only as a one-way hash. If you use Google sign-in we receive your
            name, email and a Google account identifier.
          </li>
          <li>
            <strong className="font-medium text-ink">Analysis history:</strong> for
            each analysis, the file name, the scores and the written results
            (summary, strengths, weaknesses, suggestions). Results can quote or
            paraphrase parts of your resume.
          </li>
        </ul>
        <p>
          The PDF you upload is read in memory to extract its text and is not
          stored by ResumeIQ.
        </p>
      </LegalSection>

      <LegalSection heading="How your resume is processed">
        <p>
          To produce an analysis, a rewritten resume or a cover letter, the text
          of your resume and, if you provide one, the job description are sent to
          third-party AI model providers. Do not upload anything you are not
          comfortable sharing with them, and remove sensitive details such as ID
          numbers before uploading.
        </p>
      </LegalSection>

      <LegalSection heading="Services we rely on">
        <ul className="list-disc space-y-1.5 pl-5">
          <li>Google, for optional sign-in.</li>
          <li>AI model providers, for analysis and text generation.</li>
          <li>Render, which hosts the backend and database.</li>
          <li>Vercel, which hosts the website.</li>
        </ul>
        <p>These providers process data under their own terms and privacy policies.</p>
      </LegalSection>

      <LegalSection heading="Keeping and deleting your data">
        <p>
          You can delete any past analysis yourself from the History page.
          To have your whole account and its data removed, contact me through my
          GitHub profile (github.com/M-249S) and I will delete it. During the
          beta, the database may also be reset or migrated, so keep your own
          copy of anything important.
        </p>
      </LegalSection>

      <LegalSection heading="Security">
        <p>
          Traffic uses HTTPS, passwords are hashed, and sign-in tokens expire.
          No online service can promise perfect security, and this is a small
          beta project, so please use it with that in mind.
        </p>
      </LegalSection>

      <LegalSection heading="Cookies and tracking">
        <p>
          ResumeIQ itself does not use advertising or analytics trackers. The
          Google sign-in button, when shown, is loaded from Google and is
          subject to Google&apos;s policies. Your sign-in token is kept in your
          browser&apos;s local storage so you stay logged in, and is removed when
          you log out.
        </p>
      </LegalSection>

      <LegalSection heading="Children">
        <p>ResumeIQ is not intended for anyone under 16.</p>
      </LegalSection>

      <LegalSection heading="Changes">
        <p>
          If this policy changes, the date above will change with it. Continuing
          to use ResumeIQ after an update means you accept the new version.
        </p>
      </LegalSection>
    </LegalLayout>
  );
}
