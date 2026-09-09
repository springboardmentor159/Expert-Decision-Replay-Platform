import { useEffect, useState } from "react";
import { getDecisionTimeline, getDecisionVersions, getDecisionHistory } from "../../api/decisions";
import Card from "../../components/ui/Card";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import { formatDate } from "../../utils/format";

export default function HistoryPanel({ decisionId }) {
  const [timeline, setTimeline] = useState(null);
  const [versions, setVersions] = useState(null);
  const [history, setHistory] = useState(null);
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");

  async function load() {
    setState("loading");
    try {
      const [t, v, h] = await Promise.all([
        getDecisionTimeline(decisionId),
        getDecisionVersions(decisionId),
        getDecisionHistory(decisionId),
      ]);
      setTimeline(t);
      setVersions(v);
      setHistory(h);
      setState("ready");
    } catch (err) {
      setErrorMsg(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [decisionId]);

  if (state === "loading") return <LoadingState label="Loading history…" />;
  if (state === "error") return <ErrorState message={errorMsg} onRetry={load} />;

  return (
    <div>
      <Card title="Version History">
        {versions.length === 0 ? (
          <EmptyState title="No versions recorded" />
        ) : (
          <div className="version-timeline">
            {versions.map((v) => (
              <div key={v.version_number} className="version-step">
                <div className="version-badge">v{v.version_number}</div>
                <div className="version-body">
                  <strong>{v.title}</strong>
                  <p>
                    Status: {v.status} · by User #{v.created_by} · {formatDate(v.created_at)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card title="Activity Timeline">
        {timeline.timeline.length === 0 ? (
          <EmptyState title="No timeline events yet" />
        ) : (
          <ul className="activity-list">
            {timeline.timeline.map((ev, idx) => (
              <li key={idx}>
                <span>
                  <strong>{ev.event_type}:</strong> {ev.description}
                </span>
                <span className="activity-date">{formatDate(ev.timestamp)}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card title="Change History">
        {history.history.length === 0 ? (
          <EmptyState title="No changes recorded" />
        ) : (
          <ul className="activity-list">
            {history.history.map((ev, idx) => (
              <li key={idx}>
                <span>
                  <strong>{ev.event_type}:</strong> {ev.description}
                </span>
                <span className="activity-date">{formatDate(ev.timestamp)}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
