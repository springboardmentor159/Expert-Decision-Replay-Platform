import Navbar from './Navbar';

export default function Layout({ children }) {
  return (
    <div style={styles.wrapper}>
      <Navbar />
      <main style={styles.main}>
        {children}
      </main>
    </div>
  );
}

const styles = {
  wrapper: {
    minHeight: '100vh',
    backgroundColor: '#f0f2f5',
  },
  main: {
    padding: '32px',
    maxWidth: '1400px',
    margin: '0 auto',
  },
};