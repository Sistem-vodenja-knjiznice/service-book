function main(args) {
    const title = args.title;
    const author = args.author;
    const year = args.year;
    const pages = args.pages;
    const isbn = args.isbn;
    const stock = args.stock;

    if (!title || !author || !year || !pages || !isbn || !stock) {
        return {
            "statusCode": 400,
            "body": JSON.stringify({
                message: "Missing required fields: title, author, year, pages, isbn or stock"
            })
        };
    }

    if (isbn.length !== 13) {
        return {
            "statusCode": 400,
            "body": JSON.stringify({
                message: "ISBN must be 13 characters long"
            })
        };
    }

    return {
        "statusCode": 200,
        "body": JSON.stringify({
            title: title,
            author: author,
            year: year,
            pages: pages,
            isbn: isbn,
            stock: stock
        })
    };
}


