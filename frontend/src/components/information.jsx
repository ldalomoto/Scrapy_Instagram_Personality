import { useEffect } from "react";
import { useState } from "react";
import { data, useParams } from "react-router";
import './informacion.css'

function Scrapy_Python({ username, setData }) {
    fetch(`http://127.0.0.1:8000/send-username/${username}`)
        .then((response) => response.json())
        .then((data) => {
            console.log(data),
                setData(data)
        })
        .catch((error) => console.log(error))
}

function Card_Username({ user }) {
    return (
        <>
            <div className="card_encabezado">
                <div className="card_username">
                    <div className="image">
                        <img src={`http://localhost:8000/image-proxy?url=${encodeURIComponent(user[1]["profile_pic"])}`} alt="profile" />
                    </div>
                    <div className="inf">
                        <div className="info_user">
                            <h3>{user[1]["full_name"]}</h3>
                        </div>

                        <div className="extra">
                            <h4>followers: {user[1]["followers"]}</h4>
                            <h4>following: {user[1]["following"]}</h4>
                            <h4>is_private: {user[1]["is_private"] ? "True" : "False"}</h4>
                            <h4>is_verified: {user[1]["is_verified"] ? "True" : "False"}</h4>
                            <h4>posts: {user[1]["posts"]}</h4>
                            <h4>username: {user[1]["username"]}</h4>
                        </div>
                    </div>
                </div>
                <div className="analisis_ia">
                    <div className="titulo">ANALISIS DE PERSONALIDAD</div>
                    <div className="analisis">
                        <span className="agreeableness">
                            <h3>agreeableness</h3>
                            <div className="description">
                                <h5>Score: {user[2].agreeableness.score}</h5>
                                <h4>Justification: {user[2].agreeableness.justification}</h4>
                            </div>
                        </span>
                        <span className="conscientiousness">
                            <h3>conscientiousness</h3>
                            <div className="description">
                                <h5>Score: {user[2].conscientiousness.score}</h5>
                                <h4>Justification: {user[2].conscientiousness.justification}</h4>
                            </div>
                        </span>
                        <span className="extraversion">
                            <h3>extraversion</h3>
                            <div className="description">
                                <h5>Score: {user[2].extraversion.score}</h5>
                                <h4>Justification: {user[2].extraversion.justification}</h4>
                            </div>
                        </span>
                        <span className="neuroticism">
                            <h3>neuroticism</h3>
                            <div className="description">
                                <h5>Score: {user[2].neuroticism.score}</h5>
                                <h4>Justification: {user[2].neuroticism.justification}</h4>
                            </div>
                        </span>
                        <span className="openness">
                            <h3>openness</h3>
                            <div className="description">
                                <h5>Score: {user[2].openness.score}</h5>
                                <h4>Justification: {user[2].openness.justification}</h4>
                            </div>
                        </span>
                        <span className="summary">
                            <h3>summary</h3>
                            <div className="description">
                                <h5>Score: {user[2].confidence}</h5>
                                <h4>Justification: {user[2].summary}</h4>
                            </div>
                        </span>
                    </div>
                </div>
            </div>
        </>
    );
}

function Card_Post({ user }) {
    console.log(user.media[0].url)
    return (
        <>
            <div className="post">
                <div className="post_media">
                    <video
                        src={`http://127.0.0.1:8000/media-proxy?url=${encodeURIComponent(user.media[0].url)}`}
                        controls
                    />
                </div>
                <div className="post_info">
                    <div className="post_description">
                        <h4>{user.caption}</h4>
                    </div>
                    <div className="post_comments">
                        <h3>COMMENTS</h3>
                        {user.comments.map((us) =>
                            <div className="comment">
                                <div className="section_user">
                                    <img src={`http://127.0.0.1:8000/image-proxy?url=${encodeURIComponent(us.node.owner.profile_pic_url)}`} alt="profile" />
                                    <h6 className="user_com">{us.node.owner.username}</h6>
                                </div>
                                <h6 className="user_comment">{us.node.text}</h6>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}

export default function Infor() {
    const [data, setData] = useState([]);

    const { username } = useParams();

    useEffect(() => {
        Scrapy_Python({ username, setData })
    }, [username]);

    return (
        <>
            <div>
                {data[1] &&
                    <Card_Username user={data} />}
            </div>
            <div className="contenedor_post">
                {data[0] &&
                    data[0].map((user) =>
                        <Card_Post user={user} />
                    )
                }
            </div>
        </>
    );
} 