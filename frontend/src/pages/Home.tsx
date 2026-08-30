import SearchWidget from "../components/SearchWidget";
import expressLogo from "../assets/gridrail-express-logo.jpg";

export default function Home() {
  return (
    <div className="home-page ticket-home">
      <section className="ticket-landing">
        <div className="ticket-visual">
          <img className="ticket-train-photo" src={expressLogo} alt="" />
          <div className="brand-slab">
            <div className="brand-mark">
              <span>GRIDRAIL</span>
            </div>
            <h1>GRID<br />RAIL</h1>
            <p>INDIAN RAILWAYS</p>
          </div>
          <div className="photo-caption">
            <span>100 active trains</span>
            <span>365 day journey calendar</span>
          </div>
        </div>

        <aside className="ticket-booking">
          <header>
            <div className="mini-brand">
              <img src={expressLogo} alt="" />
              GRIDRAIL
            </div>
            <small>Indian Railways</small>
          </header>
          <SearchWidget title="BOOK TICKET" landing />
          <p className="create-account">Don't have an account? <a href="/register">Create one</a></p>
        </aside>
      </section>
    </div>
  );
}
