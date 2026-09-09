export default function ErrorState({ message = "Unable to load data. Please try again.", onRetry }) {
  return (
    <div className="state-block error-state">
      <p>{message}</p>
      {onRetry && (
        <button className="btn btn-secondary btn-sm" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
