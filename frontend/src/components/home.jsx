import { useNavigate } from "react-router";
import { useState } from 'react'

export default function Home({username, setUsername, numPosts2, setNumePosts, numComments2, setNumeComments}) {
    const [user, setUser] = useState("");
    const [numPosts, setNumPosts] = useState(5);
    const [numComments, setNumComments] = useState(5);

    const navigate = useNavigate();

    const func = () => {
        setUsername(user);
        setNumePosts(numPosts);
        setNumeComments(numComments);
        navigate(`/infor/${user}/${numPosts}/${numComments}`);
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
                <h4>Ingresa el numero de posts</h4>
                <input type="number" value={5} placeholder="ingresa el numero de posts" className="username" value={numPosts} onChange={(e) => setNumPosts(e.target.value)} />
            </div>
            <div>
                <h4>Ingresa el numero de comentarios</h4>
                <input type="number" value={5} placeholder="ingresa el numero de comentarios" className="username" value={numComments} onChange={(e) => setNumComments(e.target.value)} />
            </div>
            <div>
                <button onClick={func}>INICIAR</button>
            </div>
        </>
    );
}