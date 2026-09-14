const Card = ({
  title,
  children,
  className = "",
}) => {
  return (
    <section className={`app-card ${className}`}>

      {title && (
        <div className="card-header">
          <h2>{title}</h2>
        </div>
      )}

      <div className="card-body">
        {children}
      </div>

    </section>
  );
};

export default Card;