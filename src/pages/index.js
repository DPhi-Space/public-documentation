import Link from "@docusaurus/Link"
import useDocusaurusContext from "@docusaurus/useDocusaurusContext"
import useBaseUrl from '@docusaurus/useBaseUrl'
import Layout from "@theme/Layout"
import Heading from "@theme/Heading"
import styles from "./index.module.css"

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext()
  return (
    <header className={styles.heroBanner}>
      <div className={styles.heroContainer}>
        <Heading as="h1" className={styles.heroTitle}>
          {siteConfig.title}
        </Heading>
        <p className={styles.heroSubtitle}>{siteConfig.tagline}</p>
      </div>
    </header>
  )
}

function JumpInSection() {
  const jumpInCards = [
    {
      title: "Quick Start",
      description: "Get to know Clustergate-2 and how to deploy software in Space.",
      link: "/intro/cg2",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <polygon points="10 8 16 12 10 16 10 8" />
        </svg>
      ),
    },
    {
      title: "Docker Images Onboard",
      description: "Learn through practical examples and real-world scenarios",
      link: "/specs/docker-imgs",
      icon: (
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="3" y="4" width="18" height="4" rx="1" />
          <rect x="3" y="10" width="18" height="4" rx="1" />
          <rect x="3" y="16" width="18" height="4" rx="1" />
        </svg>
      ),
    },
    {
      title: "Examples",
      description: "Browse code samples and implementation patterns to deploy in Space",
      link: "/examples/intro",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
        </svg>
      ),
    },
  ]

  return (
    <section className={styles.jumpInSection}>
      <div className={styles.container}>
        <h2 className={styles.jumpInTitle}>Jump In</h2>
        <div className={styles.jumpInGrid}>
          {jumpInCards.map((card, idx) => (
            <Link key={idx} to={useBaseUrl(card.link)} className={styles.jumpInCard}>
              <div className={styles.jumpInIcon}>{card.icon}</div>
              <h3 className={styles.jumpInCardTitle}>{card.title}</h3>
              <p className={styles.jumpInCardDescription}>{card.description}</p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}

export default function Home() {
  const { siteConfig } = useDocusaurusContext()
  return (
    <Layout title={`${siteConfig.title}`} description={siteConfig.tagline}>
      <div className={styles.pageWrapper}>
        <HomepageHeader />
        <JumpInSection />
      </div>
    </Layout>
  )
}
