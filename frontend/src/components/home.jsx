import { useNavigate } from "react-router";
import { useState } from 'react'

export default function Home({username, setUsername}) {
    const [user, setUser] = useState("");
    const navigate = useNavigate();

    const func = () => {
        setUsername(user);
        navigate(`/infor/${user}`);
    }
    return(
        <>
            <div>
                <h1>SCRAPY INSTAGRAM</h1>
            </div>
            <div>
                <h4>Ingresa el usuario a scrapear</h4>
                <input type="text" placeholder="ingresa el username" className="username" value={user} onChange={(e) => setUser(e.target.value)} />
            </div>
            <div>
                <button onClick={func}>INICIAR</button>
            </div>
        </>
    );
}